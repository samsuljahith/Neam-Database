FROM python:3.11-slim

WORKDIR /app

# Install dependencies first — Docker caches this layer separately.
# If only code changes, this step is skipped on rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model during build so the first API
# request is instant rather than waiting 2+ minutes for a download.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Persist vector indexes and SQLite db outside the container
VOLUME ["/app/data"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
