from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config.settings import settings

Base = declarative_base()

def normalize_db_url(url: str) -> str:
    if not url:
        return "sqlite+aiosqlite:///./codevita.db"
    url = url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "sslmode=" in url:
        url = url.replace("sslmode=", "ssl=")
    return url

db_url = normalize_db_url(settings.DATABASE_URL)

# SQLite needs connect_args for multithreading and concurrency
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 60.0

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args if db_url.startswith("sqlite") else {},
)

# Enable WAL (Write-Ahead Logging) and high busy timeout on SQLite to prevent "database is locked" errors
if db_url.startswith("sqlite"):
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=60000")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
