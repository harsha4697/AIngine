from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SemanticCache
from app.services.embedding_service import embedding_service
from app.database import AsyncSessionLocal # Needed for background tasks
import asyncio

# Threshold: Lower means stricter matching. 
# 0.2 is a good baseline for MiniLM-L6-v2.
SIMILARITY_THRESHOLD = 0.2

async def get_embedding_safe(prompt: str):
    """
    Helper to run CPU-bound embedding in a separate thread
    so we don't block the async event loop.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, embedding_service.embed_text, prompt)

async def find_cached_response(db: AsyncSession, prompt_text: str, current_model: str):
    """
    Checks the DB for a semantic match.
    Now includes a CRITICAL threshold filter to avoid bad matches.
    """
    # 1. Vectorize (Non-Blocking)
    prompt_vector = await get_embedding_safe(prompt_text)

    # 2. Query DB using Cosine Distance
    # We explicitly calculate the distance to filter by it.
    distance_col = SemanticCache.prompt_vector.cosine_distance(prompt_vector)

    stmt = (
        select(SemanticCache)
        .filter(SemanticCache.model_tag == current_model)
        .filter(distance_col < SIMILARITY_THRESHOLD) # <--- STOP GAP: Don't return garbage
        .order_by(distance_col)
        .limit(1)
    )
    
    result = await db.execute(stmt)
    return result.scalars().first()

async def save_to_cache_task(prompt: str, response: str, model: str):
    """
    BACKGROUND TASK: Saves interaction to DB.
    Self-contained: Opens its own DB session.
    """
    # 1. Generate Vector (CPU intensive, good to do in background)
    vector = embedding_service.embed_text(prompt)
    
    # 2. Save to DB using a fresh session
    async with AsyncSessionLocal() as db:
        new_entry = SemanticCache(
            prompt_text=prompt,
            prompt_vector=vector,
            response_text=response,
            model_tag=model
        )
        db.add(new_entry)
        await db.commit()
    
    print(f"💾 [Cache] Saved new response for: '{prompt[:20]}...'")