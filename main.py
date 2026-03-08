from fastapi import FastAPI, HTTPException
from models.schemas import (
    CreateCollectionRequest, IngestRequest,
    QueryRequest, QueryResult, ExplanationResult)
from pipeline.embedder import Embedder
from pipeline.processor import Processor
from storage.vector_store import VectorStore
from storage.metadata_store import MetadataStore
from storage.persistence import PersistenceManager

app = FastAPI(title="NEAM Vector Database",
              version="0.1.0")

embedder = Embedder()
vector_store = VectorStore()
metadata_store = MetadataStore()
processor = Processor(embedder, vector_store,
                      metadata_store)
persistence = PersistenceManager(vector_store)

@app.on_event("startup")
def startup(): persistence.load_all()

@app.on_event("shutdown")
def shutdown(): persistence.save_all()

@app.post("/collections")
def create_collection(req: CreateCollectionRequest):
    try:
        vector_store.create_collection(req.name)
        return {"message": f"Created: {req.name}"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        return processor.ingest(
            req.collection, req.text,
            req.source, req.metadata)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@app.post("/query", response_model=list[QueryResult])
def query(req: QueryRequest):
    try:
        results = processor.query(
            req.collection, req.query, req.top_k)
        return [QueryResult(
            text=r["text"], score=r["score"],
            source=r.get("source"),
            metadata=r.get("metadata"),
            explanation=r.get("explanation")
        ) for r in results]
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@app.delete("/collections/{name}")
def delete_collection(name: str):
    try:
        return processor.delete_collection(name)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@app.delete("/documents")
def delete_document(collection: str, source: str):
    try:
        return processor.delete_source(collection, source)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@app.get("/health")
def health(): return {"status": "ok"}
