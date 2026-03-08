from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Search
    default_top_k: int = 5

    # Storage
    data_dir: str = "data"

    class Config:
        env_prefix = "NEAM_"

settings = Settings()
