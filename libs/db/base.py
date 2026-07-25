from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class BaseDBModel(DeclarativeBase):
    ...


engine: AsyncEngine | None = None
Session: async_sessionmaker | None = None


def start(db_url: str, debug: bool, pool_max_size: int):
    global engine, Session
    if db_url[:db_url.find(':')] == 'postgres':
        db_url = db_url.replace('postgres', 'postgresql', 1)

    engine = create_async_engine(
        db_url.replace('postgresql', 'postgresql+asyncpg', 1),
        echo=debug,
        pool_size=pool_max_size,
    )
    Session = async_sessionmaker(bind=engine)
