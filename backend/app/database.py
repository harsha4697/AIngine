from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Docker compose credentials
DATABASE_URL = "postgresql+asyncpg://postgres:9999@localhost:5432/aingine"

engine = create_async_engine(DATABASE_URL, echo=False)

# Factory for creating new database sessions
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency for FastAPI endpoints to get a DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session  # <--- FIXED: 'session', not 'sessions'