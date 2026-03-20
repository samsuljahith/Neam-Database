import numpy as np
from config import settings
from pipeline.providers.base import BaseProvider
from pipeline.providers.local import LocalProvider

class Embedder:
    """Routes embedding to the configured provider."""

    def __init__(self):
        self.provider = self._create_provider()
        self.dimension = self.provider.get_dimension()

    def _create_provider(self) -> BaseProvider:
        """Create the right provider based on config."""
        name = settings.embedding_provider.lower()

        if name == "local":
            return LocalProvider(
                model_name=settings.embedding_model,
                dimension=settings.embedding_dimension)

        elif name == "openai":
            from pipeline.providers.openai import OpenAIProvider
            return OpenAIProvider(
                model_name=settings.embedding_model,
                api_key=settings.api_key)

        else:
            raise ValueError(
                f"Unknown provider: {name}. "
                f"Available: local, openai")

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.provider.embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        return self.provider.embed_query(query)
