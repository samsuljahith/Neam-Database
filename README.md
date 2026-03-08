# NEAM Vector Database

A lightweight, explainable vector database. Store documents, search by meaning — and understand *why* results match.

```json
{
  "score": 0.82,
  "explanation": {
    "confidence": "high",
    "matching_concepts": ["neural", "learning", "patterns"],
    "why": "Strong match. Shared concepts: neural, learning, patterns. Both texts are semantically aligned."
  }
}
```

Most vector databases return a score. NEAM tells you what it means.

---

## Quickstart

### With Docker (recommended)

```bash
docker build -t neam-db .
docker run -p 8000:8000 -v $(pwd)/data:/app/data neam-db
```

### Without Docker

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`

---

## API

### Collections

```bash
# Create
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "my-docs"}'

# List
curl http://localhost:8000/collections

# Delete
curl -X DELETE http://localhost:8000/collections/my-docs
```

### Ingest

```bash
# Text
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"collection": "my-docs", "text": "Your content here.", "source": "manual"}'

# File upload (.txt, .pdf, .csv)
curl -X POST http://localhost:8000/upload \
  -F "collection=my-docs" \
  -F "file=@report.pdf"

# Delete a document
curl -X DELETE "http://localhost:8000/documents?collection=my-docs&source=report.pdf"
```

### Query

```bash
# Search
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"collection": "my-docs", "query": "machine learning", "top_k": 5}'

# Explain a match (no collection needed)
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "text": "Neural networks learn patterns from data."}'
```

---

## How It Works

```
Upload file / text
  → Parser     extracts plain text (.txt, .pdf, .csv)
  → Chunker    splits into overlapping chunks at natural boundaries
  → Embedder   converts chunks to vectors (all-MiniLM-L6-v2)
  → FAISS      indexes vectors for fast similarity search
  → SQLite     stores chunk text and metadata
```

On query, vectors are compared by cosine similarity. Results include an explanation of confidence, matching concepts, and query coverage — generated without any LLM call.

---

## Configuration

All settings can be overridden with environment variables (prefix: `NEAM_`):

| Variable | Default | Description |
|---|---|---|
| `NEAM_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `NEAM_EMBEDDING_DIMENSION` | `384` | Must match model output |
| `NEAM_CHUNK_SIZE` | `500` | Max chars per chunk |
| `NEAM_CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `NEAM_DEFAULT_TOP_K` | `5` | Default search results |
| `NEAM_DATA_DIR` | `data` | Where indexes and DB are stored |

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/collections` | Create a collection |
| `GET` | `/collections` | List all collections |
| `DELETE` | `/collections/{name}` | Delete a collection |
| `POST` | `/ingest` | Ingest text |
| `POST` | `/upload` | Upload a file |
| `DELETE` | `/documents` | Delete by source |
| `POST` | `/query` | Semantic search |
| `POST` | `/explain` | Explain a query-text pair |
| `GET` | `/health` | Health check |

---

## Roadmap

- [ ] Multi-model support (OpenAI, Cohere, Voyage AI)
- [ ] Hybrid search (vector + BM25 keyword)
- [ ] Metadata filtering on queries
- [ ] Batch ingestion
- [ ] Web dashboard
- [ ] Authentication / API keys
- [ ] Docker Compose
- [ ] Tests and CI/CD

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
