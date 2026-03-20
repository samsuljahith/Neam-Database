# NEAM Vector Database

A lightweight, explainable vector database with hybrid search. Store documents, search by meaning — and understand *why* results match.

```json
{
  "score": 0.81,
  "search_mode": "hybrid",
  "vector_score": 0.62,
  "bm25_score": 1.0,
  "explanation": {
    "confidence": "high",
    "matching_concepts": ["neural", "learning", "patterns"],
    "why": "Strong match. Shared concepts: neural, learning, patterns. Both texts are semantically aligned."
  }
}
```

Most vector databases return a score. NEAM tells you what it means.

---

## What's New in v0.2.0

- **Hybrid search** — combine vector + BM25 keyword matching, or use either alone
- **Multi-model support** — swap between local (sentence-transformers) and OpenAI models via config
- **Web dashboard** — visual interface for search, ingestion, collections, and model management
- **CORS support** — dashboard connects directly to the API

---

## Quick Start

### With Docker (recommended)

```bash
docker build -t neam-db .
docker run -p 8000:8000 -v $(pwd)/data:/app/data neam-db
```

### Without Docker

```bash
pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```

### Web Dashboard

```bash
cd dashboard
npm install
npm run dev
# Opens at http://localhost:5173
```

API docs: http://localhost:8000/docs

---

## Hybrid Search

Three search modes, selectable per query:

```bash
# Vector — semantic similarity (FAISS)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"collection":"docs","query":"machine learning","search_mode":"vector"}'

# BM25 — exact keyword matching
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"collection":"docs","query":"machine learning","search_mode":"bm25"}'

# Hybrid — combines both (default)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"collection":"docs","query":"machine learning","search_mode":"hybrid"}'
```

Weights are configurable:
```bash
NEAM_VECTOR_WEIGHT=0.7   # default 0.5
NEAM_BM25_WEIGHT=0.3     # default 0.5
```

---

## Multi-Model Support

Switch embedding providers without changing any code:

```bash
# Local (default — free, no API key)
NEAM_EMBEDDING_PROVIDER=local
NEAM_EMBEDDING_MODEL=all-MiniLM-L6-v2    # 384d, fast
NEAM_EMBEDDING_MODEL=all-mpnet-base-v2   # 768d, better quality
NEAM_EMBEDDING_MODEL=bge-small-en-v1.5   # 384d, great for RAG

# OpenAI
NEAM_EMBEDDING_PROVIDER=openai
NEAM_EMBEDDING_MODEL=text-embedding-3-small   # 1536d
NEAM_EMBEDDING_MODEL=text-embedding-3-large   # 3072d
NEAM_API_KEY=sk-...
```

See all available models: `GET /models`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/collections` | Create a collection |
| `GET` | `/collections` | List all collections |
| `DELETE` | `/collections/{name}` | Delete a collection |
| `POST` | `/ingest` | Ingest text |
| `POST` | `/upload` | Upload a file (.txt, .pdf, .csv) |
| `DELETE` | `/documents` | Delete by source |
| `POST` | `/query` | Search (vector / bm25 / hybrid) |
| `POST` | `/explain` | Explain a query-text pair |
| `GET` | `/models` | List available embedding models |
| `GET` | `/models/current` | Show active model |
| `GET` | `/health` | Health check |

---

## Example: Full Workflow

```bash
# 1. Create a collection
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "docs"}'

# 2. Ingest text
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"collection":"docs","text":"Neural networks learn patterns from data through backpropagation.","source":"intro.txt"}'

# 3. Search (hybrid by default)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"collection":"docs","query":"how do neural networks learn?"}'

# 4. Explain without a collection
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning","text":"Neural networks learn patterns from data."}'
```

---

## How It Works

```
Upload file / text
  → Parser      extracts plain text (.txt, .pdf, .csv)
  → Chunker     splits into overlapping chunks
  → Embedder    converts chunks to vectors (local or OpenAI)
  → FAISS       indexes vectors for fast similarity search
  → BM25Store   indexes tokens for keyword search
  → SQLite      stores chunk text and metadata
```

On query, vector and BM25 scores are combined with configurable weights. Every result includes an explanation of confidence, matching concepts, and query coverage — generated without any LLM call.

---

## Configuration

All settings via environment variables (prefix: `NEAM_`):

| Variable | Default | Description |
|---|---|---|
| `NEAM_EMBEDDING_PROVIDER` | `local` | `local` or `openai` |
| `NEAM_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Model name |
| `NEAM_EMBEDDING_DIMENSION` | `384` | Must match model output |
| `NEAM_API_KEY` | — | Required for OpenAI provider |
| `NEAM_HYBRID_SEARCH` | `true` | Enable hybrid search |
| `NEAM_VECTOR_WEIGHT` | `0.5` | Weight for vector scores |
| `NEAM_BM25_WEIGHT` | `0.5` | Weight for BM25 scores |
| `NEAM_CHUNK_SIZE` | `500` | Max chars per chunk |
| `NEAM_CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `NEAM_DEFAULT_TOP_K` | `5` | Default search results |
| `NEAM_DATA_DIR` | `data` | Where indexes and DB are stored |

---

## Architecture

```
NEAM/
├── main.py                  FastAPI app, wires all components
├── config.py                Settings via env vars (NEAM_ prefix)
├── pipeline/
│   ├── embedder.py          Routes to configured provider
│   ├── providers/
│   │   ├── base.py          Abstract provider interface
│   │   ├── local.py         sentence-transformers
│   │   └── openai.py        OpenAI Embeddings API
│   ├── chunker.py           Text splitting
│   ├── processor.py         Ingest + hybrid search orchestration
│   └── explainer.py         Result explanation engine
├── storage/
│   ├── vector_store.py      FAISS index management
│   ├── bm25_store.py        BM25 keyword index
│   └── metadata_store.py    SQLite chunk metadata
├── routers/
│   ├── collections.py
│   ├── ingest.py            Text + file upload + delete
│   ├── query.py             Search + explain
│   └── models.py
└── dashboard/               React + Vite + Tailwind web UI
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
