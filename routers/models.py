from fastapi import APIRouter
from config import settings

router = APIRouter(prefix="/models", tags=["models"])

AVAILABLE_MODELS = {
    "local": {
        "provider": "local",
        "description": "Free, runs locally. No API key needed.",
        "models": [
            {
                "name": "all-MiniLM-L6-v2",
                "dimension": 384,
                "speed": "fast",
                "quality": "good",
                "default": True
            },
            {
                "name": "all-mpnet-base-v2",
                "dimension": 768,
                "speed": "medium",
                "quality": "better"
            },
            {
                "name": "bge-small-en-v1.5",
                "dimension": 384,
                "speed": "fast",
                "quality": "great for RAG"
            },
            {
                "name": "all-MiniLM-L12-v2",
                "dimension": 384,
                "speed": "medium",
                "quality": "good"
            }
        ]
    },
    "openai": {
        "provider": "openai",
        "description": "Powerful cloud models. Requires API key.",
        "models": [
            {
                "name": "text-embedding-3-small",
                "dimension": 1536,
                "speed": "fast",
                "quality": "great"
            },
            {
                "name": "text-embedding-3-large",
                "dimension": 3072,
                "speed": "medium",
                "quality": "best"
            }
        ]
    }
}

@router.get("")
def list_models():
    """List all available embedding models."""
    return {
        "current": {
            "provider": settings.embedding_provider,
            "model": settings.embedding_model,
            "dimension": settings.embedding_dimension
        },
        "available": AVAILABLE_MODELS
    }

@router.get("/current")
def current_model():
    """Show which model is currently active."""
    return {
        "provider": settings.embedding_provider,
        "model": settings.embedding_model,
        "dimension": settings.embedding_dimension
    }
