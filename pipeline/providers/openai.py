import numpy as np
import requests
from pipeline.providers.base import BaseProvider

class OpenAIProvider(BaseProvider):
    """OpenAI embedding API. Requires API key."""

    MODELS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(self, model_name: str, api_key: str):
        if model_name not in self.MODELS:
            raise ValueError(
                f"Unknown OpenAI model: {model_name}. "
                f"Available: {list(self.MODELS.keys())}")
        if not api_key:
            raise ValueError(
                "OpenAI provider requires an API key. "
                "Set NEAM_API_KEY in your environment.")
        self.model_name = model_name
        self.api_key = api_key
        self.dimension = self.MODELS[model_name]

    def embed(self, texts: list[str]) -> np.ndarray:
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model_name,
                "input": texts
            }
        )

        if response.status_code != 200:
            raise ValueError(
                f"OpenAI API error: {response.text}")

        data = response.json()
        vectors = [item["embedding"] for item in data["data"]]

        arr = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = arr / norms
        return arr

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]

    def get_dimension(self) -> int:
        return self.dimension
