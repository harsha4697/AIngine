import asyncio
from sqlalchemy import text
from app.database import engine, Base
from app.models import SemanticCache

async def init_models():
    async with engine.begin() as conn:
        # 1. Enable the pgvector extension (Crucial!)
        print("🔌 Enabling pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # 2. Drop existing tables to ensure a clean slate (Optional, but good for dev)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # 3. Create tables
        print("🏗️  Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ Database initialized successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_models())