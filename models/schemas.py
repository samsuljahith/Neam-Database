from pydantic import BaseModel
from typing import Optional

class CreateCollectionRequest(BaseModel):
    name: str

class IngestRequest(BaseModel):
    collection: str
    text: str
    source: Optional[str] = None
    metadata: Optional[dict] = None

class QueryRequest(BaseModel):
    collection: str
    query: str
    top_k: int = 5
    search_mode: Optional[str] = None  # "vector", "bm25", or "hybrid"

class ExplanationResult(BaseModel):
    confidence: str
    score_interpretation: str
    matching_concepts: list[str]
    query_coverage: float
    why: str

class QueryResult(BaseModel):
    text: str
    score: float
    source: Optional[str] = None
    metadata: Optional[dict] = None
    explanation: Optional[ExplanationResult] = None
    search_mode: Optional[str] = None
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None

class ExplainRequest(BaseModel):
    query: str
    text: str

class ExplainResponse(BaseModel):
    score: float
    explanation: ExplanationResult
