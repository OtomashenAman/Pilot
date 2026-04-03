import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://compliance:compliance@localhost:5432/compliance",
)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session
