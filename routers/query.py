from fastapi import APIRouter, HTTPException, Request
from models.schemas import QueryRequest, QueryResult

router = APIRouter(tags=["query"])

@router.post("/query", response_model=list[QueryResult])
def query(req: QueryRequest, request: Request):
    try:
        results = request.app.state.processor.query(
            req.collection, req.query, req.top_k)
        return [QueryResult(
            text=r["text"], score=r["score"],
            source=r.get("source"),
            metadata=r.get("metadata"),
            explanation=r.get("explanation")
        ) for r in results]
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
