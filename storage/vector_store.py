import faiss
import numpy as np
import os
from config import settings

class VectorStore:
    """Manages FAISS indexes for vector storage and search."""

    def __init__(self):
        self.indexes: dict[str, faiss.IndexFlatIP] = {}
        self.data_dir = settings.data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def create_collection(self, name: str):
        if name in self.indexes:
            raise ValueError(f"Collection exists: {name}")
        self.indexes[name] = faiss.IndexFlatIP(
            settings.embedding_dimension
        )

    def add(self, collection: str, vectors: np.ndarray) -> list[int]:
        """Add vectors. Returns list of assigned IDs."""
        idx = self._get(collection)
        start = idx.ntotal
        idx.add(vectors)
        return list(range(start, start + len(vectors)))

    def search(self, collection: str, query: np.ndarray,
               top_k: int = None) -> tuple[list[float], list[int]]:
        """Find similar vectors. Returns (scores, ids)."""
        idx = self._get(collection)
        k = min(top_k or settings.default_top_k, idx.ntotal)
        if k == 0: return [], []
        scores, ids = idx.search(query.reshape(1, -1), k)
        return scores[0].tolist(), ids[0].tolist()

    def save(self, collection: str):
        idx = self._get(collection)
        faiss.write_index(idx, os.path.join(
            self.data_dir, f"{collection}.index"))

    def load(self, collection: str):
        path = os.path.join(self.data_dir, f"{collection}.index")
        if os.path.exists(path):
            self.indexes[collection] = faiss.read_index(path)

    def _get(self, name: str) -> faiss.IndexFlatIP:
        if name not in self.indexes:
            raise ValueError(f"Collection not found: {name}")
        return self.indexes[name]
