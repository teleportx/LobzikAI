import asyncio
import weakref
from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator

import aiormq
from aiormq.abc import AbstractConnection, AbstractChannel
from loguru import logger

from libs import config


class BrokerConnectionManager:
    def __init__(
            self,
            url: str,
            pool_size: int = 16,
            reconnect_delay: float = 5.0,
            health_check_interval: float = 15.0,
            health_check_timeout: float = 5.0,
            connect_timeout: float = 10.0,
            close_timeout: float = 5.0,
    ) -> None:
        self._url = url
        self._pool_size = pool_size
        self._reconnect_delay = reconnect_delay
        self._health_check_interval = health_check_interval
        self._health_check_timeout = health_check_timeout
        self._connect_timeout = connect_timeout
        self._close_timeout = close_timeout

        self._connection: AbstractConnection | None = None
        self._connection_lock = asyncio.Lock()

        self._owners: weakref.WeakKeyDictionary[
            AbstractChannel, AbstractConnection
        ] = weakref.WeakKeyDictionary()

        self._pool: asyncio.Queue[AbstractChannel | None] = asyncio.Queue()
        for _ in range(self._pool_size):
            self._pool.put_nowait(None)

        self._wake = asyncio.Event()
        self._watchdog_task: asyncio.Task | None = None

    # ------------------------------------------------------------------ #
    # lifecycle
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        await self.get_connection()

        if self._watchdog_task is None or self._watchdog_task.done():
            self._watchdog_task = asyncio.create_task(
                self._watchdog(),
                name='broker-connection-watchdog',
            )

    async def stop(self) -> None:
        task, self._watchdog_task = self._watchdog_task, None
        if task is not None:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

        drained = 0
        channels: list[AbstractChannel] = []
        while True:
            try:
                slot = self._pool.get_nowait()
            except asyncio.QueueEmpty:
                break
            drained += 1
            if slot is not None:
                channels.append(slot)

        for channel in channels:
            await self._safe_close(channel)

        connection, self._connection = self._connection, None
        if connection is not None:
            await self._safe_close(connection)

        for _ in range(drained):
            self._pool.put_nowait(None)

    # ------------------------------------------------------------------ #
    # connection
    # ------------------------------------------------------------------ #

    async def _safe_close(self, obj: AbstractConnection | AbstractChannel) -> None:
        try:
            if obj.is_closed:
                return
            await asyncio.wait_for(obj.close(), self._close_timeout)
        except Exception:
            logger.debug('Error while closing %r', obj, exc_info=True)

    async def _connect(self) -> AbstractConnection:
        while True:
            try:
                return await asyncio.wait_for(
                    aiormq.connect(self._url),
                    self._connect_timeout,
                )
            except Exception:
                logger.exception('Error while aiormq connecting')
                await asyncio.sleep(self._reconnect_delay)

    async def get_connection(self) -> AbstractConnection:
        connection = self._connection
        if connection is not None and not connection.is_closed:
            return connection

        async with self._connection_lock:
            connection = self._connection
            if connection is not None and not connection.is_closed:
                return connection

            logger.info('Connecting to broker')
            self._connection = await self._connect()
            logger.info('Connected to broker')
            return self._connection

    async def _drop_connection(self, connection: AbstractConnection) -> None:
        async with self._connection_lock:
            if self._connection is connection:
                self._connection = None

        await self._safe_close(connection)

    # ------------------------------------------------------------------ #
    # health check
    # ------------------------------------------------------------------ #

    async def _probe(self, connection: AbstractConnection) -> None:
        channel = await connection.channel()
        try:
            await channel.basic_qos(prefetch_count=0)
        finally:
            if not channel.is_closed:
                try:
                    await channel.close()
                except Exception:
                    pass

    async def _check_health(self) -> None:
        connection = self._connection

        if connection is None or connection.is_closed:
            logger.warning('Broker connection is closed, reconnecting')
            await self.get_connection()
            return

        try:
            await asyncio.wait_for(
                self._probe(connection),
                self._health_check_timeout,
            )
        except Exception:
            logger.warning(
                'Broker health check failed, reconnecting',
                exc_info=True,
            )
            await self._drop_connection(connection)
            await self.get_connection()

    async def _watchdog(self) -> None:
        while True:
            try:
                try:
                    await asyncio.wait_for(
                        self._wake.wait(),
                        self._health_check_interval,
                    )
                except asyncio.TimeoutError:
                    pass
                self._wake.clear()

                await self._check_health()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception('Broker watchdog iteration failed')
                await asyncio.sleep(self._reconnect_delay)

    # ------------------------------------------------------------------ #
    # channels
    # ------------------------------------------------------------------ #

    async def _create_channel(self) -> AbstractChannel:
        connection = await self.get_connection()

        channel = await asyncio.wait_for(
            connection.channel(publisher_confirms=True),
            self._health_check_timeout,
        )
        self._owners[channel] = connection
        return channel

    async def _validate_channel(
            self,
            channel: AbstractChannel | None,
    ) -> AbstractChannel:
        if channel is None or channel.is_closed:
            return await self._create_channel()

        connection = self._connection
        if connection is None or connection.is_closed:
            return await self._create_channel()

        if self._owners.get(channel) is not connection:
            return await self._create_channel()

        return channel

    def is_channel_alive(self, channel: AbstractChannel) -> bool:
        connection = self._connection
        return (
                not channel.is_closed
                and connection is not None
                and not connection.is_closed
                and self._owners.get(channel) is connection
        )

    @asynccontextmanager
    async def acquire_channel(self) -> AsyncIterator[AbstractChannel]:
        slot = await self._pool.get()
        channel: AbstractChannel | None = slot

        try:
            channel = await self._validate_channel(slot)
            yield channel
        except Exception:

            self._wake.set()
            raise
        finally:

            if channel is not None and not channel.is_closed:
                self._pool.put_nowait(channel)
            else:
                self._pool.put_nowait(None)


class ConnectionStorer:
    _connection: Optional[AbstractConnection] = None
    _channel: Optional[AbstractChannel] = None

    async def get_connection(self) -> Optional[AbstractConnection]:
        if self._connection is None or self._connection.is_closed:
            self._connection = await aiormq.connect(config.amqp_url)
        return self._connection

    async def get_channel(self) -> Optional[AbstractChannel]:
        if self._channel is None or self._channel.is_closed:
            self._channel = await (await self.get_connection()).channel()
        return self._channel


storer = ConnectionStorer()
