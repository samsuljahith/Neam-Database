import numpy as np
from pipeline.chunker import Chunker
from pipeline.embedder import Embedder
from pipeline.explainer import Explainer
from storage.vector_store import VectorStore
from storage.metadata_store import MetadataStore

class Processor:
    """Orchestrates: text -> chunk -> embed -> store."""

    def __init__(self, embedder, vector_store, metadata_store):
        self.chunker = Chunker()
        self.embedder = embedder
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.explainer = Explainer()

    def ingest(self, collection, text, source=None,
               metadata=None):
        chunks = self.chunker.chunk(text)
        if not chunks:
            return {"chunks_stored": 0}

        vectors = self.embedder.embed(chunks)
        vector_ids = self.vector_store.add(collection, vectors)

        for chunk_text, vid in zip(chunks, vector_ids):
            self.metadata_store.add(
                collection=collection, vector_id=vid,
                text=chunk_text, source=source,
                metadata=metadata)

        self.vector_store.save(collection)
        return {"chunks_stored": len(chunks),
                "vector_ids": vector_ids}

    def query(self, collection, query_text, top_k=None):
        qv = self.embedder.embed_query(query_text)
        scores, ids = self.vector_store.search(
            collection, qv, top_k)

        valid = [i for i in ids if i >= 0]
        if not valid: return []

        results = self.metadata_store.get_by_vector_ids(
            collection, valid)

        score_map = dict(zip(ids, scores))
        for r in results:
            r["score"] = score_map.get(r["vector_id"], 0)
            r["explanation"] = self.explainer.explain(
                query_text, r["text"], r["score"])

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def delete_source(self, collection: str, source: str) -> dict:
        """Delete all chunks from a specific source, then rebuild the index."""
        deleted_ids = self.metadata_store.delete_by_source(collection, source)
        if not deleted_ids:
            return {"deleted": 0}

        remaining = self.metadata_store.get_all_for_rebuild(collection)
        if remaining:
            texts = [r["text"] for r in remaining]
            vectors = self.embedder.embed(texts)
            new_ids = self.vector_store.rebuild(collection, vectors)
            # Remap SQLite vector_ids to match the new FAISS positions
            for row, new_id in zip(remaining, new_ids):
                self.metadata_store.conn.execute(
                    "UPDATE chunks SET vector_id=? WHERE id=?",
                    (new_id, row["id"]))
            self.metadata_store.conn.commit()
        else:
            self.vector_store.rebuild(collection, np.empty((0, self.embedder.dimension), dtype=np.float32))

        self.vector_store.save(collection)
        return {"deleted": len(deleted_ids)}

    def delete_collection(self, collection: str) -> dict:
        """Delete entire collection from both stores."""
        self.metadata_store.delete_collection(collection)
        self.vector_store.delete_collection(collection)
        return {"message": f"Deleted collection: {collection}"}
