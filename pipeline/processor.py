import numpy as np
from pipeline.chunker import Chunker
from pipeline.explainer import Explainer
from config import settings

class Processor:
    """Orchestrates: text -> chunk -> embed -> store."""

    def __init__(self, embedder, vector_store,
                 metadata_store, bm25_store=None):
        self.chunker = Chunker()
        self.embedder = embedder
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.bm25_store = bm25_store
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

            if self.bm25_store:
                self.bm25_store.add(collection, vid, chunk_text)

        self.vector_store.save(collection)
        return {"chunks_stored": len(chunks),
                "vector_ids": vector_ids}

    def query(self, collection, query_text, top_k=None,
              search_mode=None):
        """Search with vector, BM25, or hybrid."""
        k = top_k or settings.default_top_k

        mode = search_mode or (
            "hybrid" if settings.hybrid_search
            and self.bm25_store else "vector")

        if mode == "vector":
            return self._vector_search(collection, query_text, k)
        elif mode == "bm25":
            return self._bm25_search(collection, query_text, k)
        else:
            return self._hybrid_search(collection, query_text, k)

    def _vector_search(self, collection, query_text, top_k):
        qv = self.embedder.embed_query(query_text)
        scores, ids = self.vector_store.search(
            collection, qv, top_k)

        valid = [i for i in ids if i >= 0]
        if not valid:
            return []

        results = self.metadata_store.get_by_vector_ids(
            collection, valid)

        score_map = dict(zip(ids, scores))
        for r in results:
            r["score"] = score_map.get(r["vector_id"], 0)
            r["explanation"] = self.explainer.explain(
                query_text, r["text"], r["score"])
            r["search_mode"] = "vector"

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

<<<<<<< HEAD
    def delete_source(self, collection: str, source: str) -> dict:
        """Delete all chunks from a specific source, then rebuild the index."""
        deleted_ids = self.metadata_store.delete_by_source(collection, source)
=======
    def _bm25_search(self, collection, query_text, top_k):
        if not self.bm25_store:
            raise ValueError("BM25 search not available")

        bm25_results = self.bm25_store.search(
            collection, query_text, top_k)

        if not bm25_results:
            return []

        vids = [vid for vid, _ in bm25_results]
        results = self.metadata_store.get_by_vector_ids(
            collection, vids)

        bm25_map = dict(bm25_results)
        for r in results:
            r["score"] = bm25_map.get(r["vector_id"], 0)
            r["explanation"] = self.explainer.explain(
                query_text, r["text"], r["score"])
            r["search_mode"] = "bm25"

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _hybrid_search(self, collection, query_text, top_k):
        qv = self.embedder.embed_query(query_text)
        v_scores, v_ids = self.vector_store.search(
            collection, qv, top_k * 2)

        bm25_results = self.bm25_store.search(
            collection, query_text, top_k * 2)

        bm25_map = dict(bm25_results)
        max_bm25 = max(bm25_map.values()) if bm25_map else 1
        if max_bm25 > 0:
            bm25_map = {k: v / max_bm25
                        for k, v in bm25_map.items()}

        all_vids = set()
        v_score_map = {}
        for vid, score in zip(v_ids, v_scores):
            if vid >= 0:
                all_vids.add(vid)
                v_score_map[vid] = score

        for vid in bm25_map:
            all_vids.add(vid)

        if not all_vids:
            return []

        vw = settings.vector_weight
        bw = settings.bm25_weight

        hybrid_scores = {
            vid: (v_score_map.get(vid, 0) * vw) + (bm25_map.get(vid, 0) * bw)
            for vid in all_vids
        }

        ranked_vids = sorted(hybrid_scores,
                             key=lambda x: hybrid_scores[x],
                             reverse=True)[:top_k]

        results = self.metadata_store.get_by_vector_ids(
            collection, list(ranked_vids))

        for r in results:
            vid = r["vector_id"]
            r["score"] = hybrid_scores.get(vid, 0)
            r["vector_score"] = v_score_map.get(vid, 0)
            r["bm25_score"] = bm25_map.get(vid, 0)
            r["explanation"] = self.explainer.explain(
                query_text, r["text"], r["score"])
            r["search_mode"] = "hybrid"

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def delete_source(self, collection, source):
        deleted_ids = self.metadata_store.delete_by_source(
            collection, source)

>>>>>>> 57b6836 (feat: add BM25 engine and hybrid search (vector + keyword))
        if not deleted_ids:
            return {"deleted": 0}

        remaining = self.metadata_store.get_all_for_rebuild(collection)
<<<<<<< HEAD
=======

>>>>>>> 57b6836 (feat: add BM25 engine and hybrid search (vector + keyword))
        if remaining:
            texts = [r["text"] for r in remaining]
            vectors = self.embedder.embed(texts)
            new_ids = self.vector_store.rebuild(collection, vectors)
<<<<<<< HEAD
            # Remap SQLite vector_ids to match the new FAISS positions
            for row, new_id in zip(remaining, new_ids):
                self.metadata_store.conn.execute(
                    "UPDATE chunks SET vector_id=? WHERE id=?",
                    (new_id, row["id"]))
            self.metadata_store.conn.commit()
        else:
            self.vector_store.rebuild(collection, np.empty((0, self.embedder.dimension), dtype=np.float32))
=======

            for row, new_id in zip(remaining, new_ids):
                self.metadata_store.conn.execute(
                    "UPDATE chunks SET vector_id=? WHERE id=?",
                    (new_id, row.get("id") or row["vector_id"]))
            self.metadata_store.conn.commit()

            if self.bm25_store:
                docs = [(nid, r["text"])
                        for nid, r in zip(new_ids, remaining)]
                self.bm25_store.rebuild(collection, docs)
        else:
            self.vector_store.rebuild(
                collection,
                np.empty((0, self.embedder.dimension), dtype=np.float32))
            if self.bm25_store:
                self.bm25_store.create_collection(collection)
>>>>>>> 57b6836 (feat: add BM25 engine and hybrid search (vector + keyword))

        self.vector_store.save(collection)
        return {"deleted": len(deleted_ids)}

<<<<<<< HEAD
    def delete_collection(self, collection: str) -> dict:
        """Delete entire collection from both stores."""
        self.metadata_store.delete_collection(collection)
        self.vector_store.delete_collection(collection)
=======
    def delete_collection(self, collection):
        self.metadata_store.delete_collection(collection)
        self.vector_store.delete_collection(collection)
        if self.bm25_store and collection in self.bm25_store.collections:
            del self.bm25_store.collections[collection]
>>>>>>> 57b6836 (feat: add BM25 engine and hybrid search (vector + keyword))
        return {"message": f"Deleted collection: {collection}"}
