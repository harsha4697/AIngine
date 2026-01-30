from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

class SemanticCache(Base):
    __tablename__ = "semantic_cache"

    id = Column(Integer, primary_key=True, index=True)
    prompt_text = Column(Text, nullable=False)
    # 384 dimensions matches our all-MiniLM-L6-v2 model
    prompt_vector = Column(Vector(384), nullable=False) 
    response_text = Column(Text, nullable=False)
    model_tag = Column(String, nullable=False) # e.g., 'Qwen-32B'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # We will verify the index creation in the init script

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # e.g. "My Mobile App"
    key_prefix = Column(String, nullable=False) # First 8 chars for display (e.g. "sk-1234...")
    key_hash = Column(String, nullable=False) # The secret hashed
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Optional: Scope permissions (e.g. "read", "write")
    # scopes = Column(String, default="generate")