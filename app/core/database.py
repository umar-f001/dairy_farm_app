from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from typing import AsyncGenerator

DB_url = "postgresql+asyncpg://postgres:12345678@localhost:5432/postgres"

engine = create_async_engine(DB_url, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()