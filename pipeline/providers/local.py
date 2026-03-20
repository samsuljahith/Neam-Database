from sentence_transformers import SentenceTransformer
import numpy as np
from pipeline.providers.base import BaseProvider

class LocalProvider(BaseProvider):
    """Free, local embedding using sentence-transformers."""

    def __init__(self, model_name: str, dimension: int):
        self.model = SentenceTransformer(model_name)
        self.dimension = dimension

    def embed(self, texts: list[str]) -> np.ndarray:
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]

    def get_dimension(self) -> int:
        return self.dimension
