from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline.embedder import Embedder
from pipeline.processor import Processor
from storage.vector_store import VectorStore
from storage.metadata_store import MetadataStore
from storage.persistence import PersistenceManager
from storage.bm25_store import BM25Store
from routers import collections, ingest, query, models

app = FastAPI(title="NEAM Vector Database", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedder = Embedder()
vector_store = VectorStore()
metadata_store = MetadataStore()
bm25_store = BM25Store()
processor = Processor(embedder, vector_store, metadata_store, bm25_store)
persistence = PersistenceManager(vector_store)

app.state.processor = processor
app.state.vector_store = vector_store
app.state.metadata_store = metadata_store
app.state.bm25_store = bm25_store

app.include_router(collections.router)
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(models.router)

@app.on_event("startup")
def startup(): persistence.load_all()

@app.on_event("shutdown")
def shutdown(): persistence.save_all()

@app.get("/health")
def health(): return {"status": "ok"}
