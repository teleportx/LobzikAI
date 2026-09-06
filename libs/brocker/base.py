import asyncio
from contextlib import asynccontextmanager
from typing import Optional

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
    ) -> None:
        self._url = url
        self._pool_size = pool_size
        self._reconnect_delay = reconnect_delay

        self._connection: AbstractConnection | None = None

        self._connection_lock = asyncio.Lock()
        self._pool_init_lock = asyncio.Lock()

        self._pool: asyncio.Queue[AbstractChannel] = asyncio.Queue()
        self._pool_initialized = False

    async def start(self) -> None:
        await self._ensure_pool()

    async def stop(self) -> None:
        channels = []

        while not self._pool.empty():
            try:
                channels.append(self._pool.get_nowait())
            except asyncio.QueueEmpty:
                break

        for channel in channels:
            try:
                if not channel.is_closed:
                    await channel.close()
            except Exception:
                pass

        if self._connection and not self._connection.is_closed:
            try:
                await self._connection.close()
            except Exception:
                pass

        self._connection = None
        self._pool_initialized = False

    async def _connect(self) -> AbstractConnection:
        while True:
            try:
                return await aiormq.connect(self._url)
            except Exception:
                logger.exception('Error while aiormq connecting')
                await asyncio.sleep(self._reconnect_delay)

    async def get_connection(self) -> AbstractConnection:
        if self._connection and not self._connection.is_closed:
            return self._connection

        async with self._connection_lock:
            if self._connection and not self._connection.is_closed:
                return self._connection

            self._connection = await self._connect()

            self._pool_initialized = False

            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except asyncio.QueueEmpty:
                    break

            return self._connection

    async def _create_channel(self) -> AbstractChannel:
        connection = await self.get_connection()

        channel = await connection.channel(
            publisher_confirms=True,
        )

        return channel

    async def _ensure_pool(self) -> None:
        if self._pool_initialized:
            return

        async with self._pool_init_lock:
            if self._pool_initialized:
                return

            await self.get_connection()

            for _ in range(self._pool_size):
                channel = await self._create_channel()
                await self._pool.put(channel)

            self._pool_initialized = True

    async def _validate_channel(
        self,
        channel: AbstractChannel,
    ) -> AbstractChannel:
        if channel.is_closed:
            return await self._create_channel()

        if self._connection is None:
            return await self._create_channel()

        if self._connection.is_closed:
            return await self._create_channel()

        return channel

    @asynccontextmanager
    async def acquire_channel(self):
        await self._ensure_pool()

        channel = await self._pool.get()

        try:
            channel = await self._validate_channel(channel)
            yield channel
        finally:
            if not channel.is_closed:
                await self._pool.put(channel)


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
