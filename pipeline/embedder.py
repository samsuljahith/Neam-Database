from sentence_transformers import SentenceTransformer
import numpy as np
from config import settings

class Embedder:
    """Converts text strings into dense vectors."""

    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.dimension = settings.embedding_dimension

    def embed(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of texts. Returns (N, dimension) array."""
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string."""
        return self.embed([query])[0]
