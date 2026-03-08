from fastapi import FastAPI
from pipeline.embedder import Embedder
from pipeline.processor import Processor
from storage.vector_store import VectorStore
from storage.metadata_store import MetadataStore
from storage.persistence import PersistenceManager
from routers import collections, ingest, query

app = FastAPI(title="NEAM Vector Database",
              version="0.1.0")

# Wire components
embedder = Embedder()
vector_store = VectorStore()
metadata_store = MetadataStore()
processor = Processor(embedder, vector_store, metadata_store)
persistence = PersistenceManager(vector_store)

# Store on app state for routers
app.state.processor = processor
app.state.vector_store = vector_store
app.state.metadata_store = metadata_store

# Register routers
app.include_router(collections.router)
app.include_router(ingest.router)
app.include_router(query.router)

@app.on_event("startup")
def startup(): persistence.load_all()

@app.on_event("shutdown")
def shutdown(): persistence.save_all()

@app.get("/health")
def health(): return {"status": "ok"}
