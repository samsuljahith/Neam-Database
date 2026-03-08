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
