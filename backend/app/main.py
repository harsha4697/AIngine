from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional, List
import asyncio

# --- App Imports ---
from app.database import get_db
from app.services.model_manager import model_manager
from app.services.cache_service import find_cached_response, save_to_cache_task 
from app.services.auth_service import auth_service, get_current_api_key
from app.models import APIKey

app = FastAPI(title="AI Platform Core", version="1.0.0")

# --- 1. CORS Middleware ---
# Allows your Next.js frontend (localhost:3000) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- 🔐 CLOUD SECURITY CONFIG ---
# This is the password your Cloud Gateway must send to access the GPU.
# In a real production env, you should set this via os.getenv("LOCAL_SECRET")
LOCAL_SECRET = "super-secret-bridge-token-123"

# --- 🔒 GLOBAL GPU LOCK ---
# Ensures only ONE request touches the GPU at a time to prevent vLLM crashes.
gpu_lock = asyncio.Lock()

# --- Pydantic Models ---
class LoadModelRequest(BaseModel):
    model_id: str
    model_path: str
    quantization: Optional[str] = "awq" # Supports 'None' for standard weights

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 200

class CreateKeyRequest(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    prefix: str
    created: str

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "current_model": model_manager.current_model_name,
        "gpu_locked": gpu_lock.locked() 
    }

# --- 🔑 API Key Management (Admin Only) ---

@app.post("/admin/keys")
async def create_api_key(request: CreateKeyRequest, db: AsyncSession = Depends(get_db)):
    """
    Generates a new API Key. 
    Returns the raw key ONCE. It cannot be retrieved again.
    """
    raw_key, prefix, key_hash = auth_service.generate_key()
    
    new_key = APIKey(
        name=request.name,
        key_prefix=prefix,
        key_hash=key_hash
    )
    db.add(new_key)
    await db.commit()
    
    return {
        "name": request.name, 
        "api_key": raw_key, 
        "message": "⚠️ SAVE THIS KEY. It will not be shown again."
    }

@app.get("/admin/keys")
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    """Lists active keys (hides the actual secret)."""
    result = await db.execute(select(APIKey).filter(APIKey.is_active == True))
    keys = result.scalars().all()
    # Simple serialization
    return [
        {
            "id": k.id, 
            "name": k.name, 
            "prefix": k.key_prefix, 
            "created": str(k.created_at)
        } for k in keys
    ]

@app.delete("/admin/keys/{key_id}")
async def revoke_api_key(key_id: int, db: AsyncSession = Depends(get_db)):
    """Revokes a key so it can no longer be used."""
    key = await db.get(APIKey, key_id)
    if key:
        key.is_active = False
        await db.commit()
        return {"status": "revoked", "id": key_id}
    raise HTTPException(status_code=404, detail="Key not found")


# --- 🧠 Model Management ---

@app.post("/admin/load-model")
async def load_model_endpoint(request: LoadModelRequest):
    """
    Triggers a model swap.
    Acquires the lock to ensure no generation is happening while swapping.
    """
    async with gpu_lock:
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: model_manager.load_model(
                    model_path=request.model_path,
                    model_id=request.model_id,
                    quantization=request.quantization
                )
            )
            return {"status": "success", "message": f"Loaded {request.model_id}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- 💬 Inference (Secured) ---

@app.post("/generate")
async def generate_text(
    request: GenerateRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    # 👇 SECURITY CHECK: 
    # 1. Checks for 'x-internal-secret' (from Cloud Gateway)
    # 2. OR checks for 'api_key' (if you enable it later for direct access)
    x_internal_secret: Optional[str] = Header(None)
):
    # --- 1. Cloud Tunnel Security ---
    # Only allow requests that have the correct "Secret Handshake"
    if x_internal_secret != LOCAL_SECRET:
        print(f"🛑 Unauthorized access attempt. Token: {x_internal_secret}")
        raise HTTPException(status_code=403, detail="Unauthorized GPU Access. Missing Secret.")

    # --- 2. Model Check ---
    if not model_manager.llm:
        raise HTTPException(status_code=400, detail="No model loaded.")
    
    current_model = model_manager.current_model_name

    # --- 3. Cache Check (Semantic Search) ---
    # Uncomment when ready to use caching
    """
    cached_entry = await find_cached_response(db, request.prompt, current_model)
    if cached_entry:
        return {
            "response": cached_entry.response_text, 
            "model_used": current_model,
            "source": "cache ⚡" 
        }
    """

    # --- 4. Inference ---
    try:
        async with gpu_lock:
            loop = asyncio.get_event_loop()
            generated_text = await loop.run_in_executor(
                None, 
                model_manager.generate, 
                request.prompt, 
                request.max_tokens
            )
        
        # 5. Save to Cache
        background_tasks.add_task(
            save_to_cache_task, 
            request.prompt, 
            generated_text, 
            current_model
        )

        return {
            "response": generated_text, 
            "model_used": current_model,
            "source": "gpu 🐢"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))