from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

import config


class BaseDBModel(DeclarativeBase):
    ...


engine: AsyncEngine | None = None
Session: async_sessionmaker | None = None


def start():
    global engine, Session
    engine = create_async_engine(
        config.db_url.replace('postgresql', 'postgresql+asyncpg'),
        echo=config.debug,
        pool_size=config.Constants.db_pool_max_size
    )
    Session = async_sessionmaker(bind=engine)
