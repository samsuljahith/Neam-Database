from fastapi import APIRouter, HTTPException, Request
from models.schemas import (
    QueryRequest, QueryResult,
    ExplainRequest, ExplainResponse)

router = APIRouter(tags=["query"])

@router.post("/query", response_model=list[QueryResult])
def query(req: QueryRequest, request: Request):
    try:
        results = request.app.state.processor.query(
            req.collection, req.query, req.top_k,
            req.search_mode)
        return [QueryResult(
            text=r["text"], score=r["score"],
            source=r.get("source"),
            metadata=r.get("metadata"),
            explanation=r.get("explanation"),
            search_mode=r.get("search_mode"),
            vector_score=r.get("vector_score"),
            bm25_score=r.get("bm25_score")
        ) for r in results]
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest, request: Request):
    """Explain why a query matches a text — no collection needed."""
    try:
        processor = request.app.state.processor
        query_vec = processor.embedder.embed_query(req.query)
        text_vec = processor.embedder.embed_query(req.text)
        score = float(query_vec @ text_vec)
        explanation = processor.explainer.explain(
            req.query, req.text, score)
        return ExplainResponse(
            score=round(score, 4),
            explanation=explanation)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
