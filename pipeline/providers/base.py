from abc import ABC, abstractmethod
import numpy as np

class BaseProvider(ABC):
    """Every embedding provider must follow these rules."""

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts. Returns (N, dimension) array."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query. Returns (dimension,) array."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the embedding dimension for this model."""
        pass
