import secrets
import hashlib
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from app.models import APIKey
from app.database import get_db

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

class AuthService:
    def generate_key(self):
        """Generates a secure random key like 'sk-live-...'"""
        raw_key = f"sk-live-{secrets.token_urlsafe(32)}"
        prefix = raw_key[:12]
        # Hash it for storage
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, prefix, hashed_key

    def verify_key_hash(self, raw_key: str, hashed_key: str) -> bool:
        """Compares incoming key with stored hash"""
        input_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return secrets.compare_digest(input_hash, hashed_key)

auth_service = AuthService()

# --- DEPENDENCY FOR PROTECTED ROUTES ---
async def get_current_api_key(
    api_key_header: str = Security(API_KEY_HEADER),
    db: AsyncSession = Depends(get_db)
):
    if not api_key_header:
        raise HTTPException(status_code=403, detail="Missing X-API-Key header")

    # 1. Hash the incoming key to look it up
    input_hash = hashlib.sha256(api_key_header.encode()).hexdigest()

    # 2. Find in DB
    result = await db.execute(select(APIKey).filter(APIKey.key_hash == input_hash, APIKey.is_active == True))
    key_record = result.scalars().first()

    if not key_record:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    return key_record