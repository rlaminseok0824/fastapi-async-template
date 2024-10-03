from functools import lru_cache
from typing import Any, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncConnection,AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.settings import settings

class Base(DeclarativeBase):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    # To prevent implicit I/O when using AsyncSession, you can set eager_defaults=True on the __mapper_args__ of your model classes.
    # created_at 과 같이 비동기로 값에 접근하기 위해선 eager_defaults=True 를 설정해야 한다.
    __mapper_args__ = {"eager_defaults": True}

class DatabaseSessionManager:
    # sqlalchemy 에선 ORM을 위하여 session을 바탕으로 데이터 전개한다.
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autoflush=False,bind=self._engine,expire_on_commit=False,autocommit=False)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = DatabaseSessionManager(settings.SQLALCHEMY_DATABASE_URI)

async def get_db_session():
    async with session_manager.session() as session:
        yield session