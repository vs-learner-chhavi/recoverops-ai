"""
RecoverOps AI — Database Layer
SQLAlchemy async engine with SQLite / PostgreSQL support.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Use aiosqlite for local development, asyncpg for production PostgreSQL
if "sqlite" in settings.database_url:
    engine = create_async_engine(
        settings.database_url,
        echo=False,  # <-- Set to False to disable raw SQL query spam
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=20,
        max_overflow=10,
    )

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency injection for FastAPI routes."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
