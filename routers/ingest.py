from fastapi import APIRouter, HTTPException, Request
from models.schemas import IngestRequest

router = APIRouter(tags=["ingest"])

@router.post("/ingest")
def ingest(req: IngestRequest, request: Request):
    try:
        return request.app.state.processor.ingest(
            req.collection, req.text,
            req.source, req.metadata)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/documents")
def delete_document(collection: str, source: str, request: Request):
    try:
        return request.app.state.processor.delete_source(
            collection, source)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
