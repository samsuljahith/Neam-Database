from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Embedding provider
    embedding_provider: str = "local"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    api_key: Optional[str] = None

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Search
    default_top_k: int = 5
    hybrid_search: bool = True
    vector_weight: float = 0.5
    bm25_weight: float = 0.5

    # Storage
    data_dir: str = "data"

    class Config:
        env_prefix = "NEAM_"

settings = Settings()
