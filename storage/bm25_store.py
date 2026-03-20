import math
from collections import Counter

class BM25Store:
    """BM25 keyword search engine."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.collections: dict[str, dict] = {}

    def create_collection(self, name: str):
        """Initialize a BM25 collection."""
        self.collections[name] = {
            "docs": {},
            "doc_lengths": {},
            "avg_doc_length": 0,
            "doc_count": 0,
            "df": Counter()
        }

    def add(self, collection: str, vector_id: int, text: str):
        """Add a document to the BM25 index."""
        coll = self._get(collection)
        tokens = self._tokenize(text)
        coll["docs"][vector_id] = tokens
        coll["doc_lengths"][vector_id] = len(tokens)

        unique_tokens = set(tokens)
        for token in unique_tokens:
            coll["df"][token] += 1

        coll["doc_count"] += 1
        total = sum(coll["doc_lengths"].values())
        coll["avg_doc_length"] = total / coll["doc_count"]

    def search(self, collection: str, query: str,
               top_k: int = 5) -> list[tuple[int, float]]:
        """Search using BM25. Returns [(vector_id, score), ...]."""
        coll = self._get(collection)
        if coll["doc_count"] == 0:
            return []

        query_tokens = self._tokenize(query)
        scores = {}

        for vid, doc_tokens in coll["docs"].items():
            score = self._score_document(
                coll, query_tokens, doc_tokens, vid)
            if score > 0:
                scores[vid] = score

        ranked = sorted(scores.items(),
                        key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def remove(self, collection: str, vector_id: int):
        """Remove a document from BM25 index."""
        coll = self._get(collection)
        if vector_id in coll["docs"]:
            tokens = coll["docs"][vector_id]
            for token in set(tokens):
                coll["df"][token] -= 1
                if coll["df"][token] <= 0:
                    del coll["df"][token]

            del coll["docs"][vector_id]
            del coll["doc_lengths"][vector_id]
            coll["doc_count"] -= 1

            if coll["doc_count"] > 0:
                total = sum(coll["doc_lengths"].values())
                coll["avg_doc_length"] = total / coll["doc_count"]
            else:
                coll["avg_doc_length"] = 0

    def rebuild(self, collection: str,
                documents: list[tuple[int, str]]):
        """Rebuild BM25 index from scratch."""
        self.create_collection(collection)
        for vid, text in documents:
            self.add(collection, vid, text)

    def _score_document(self, coll, query_tokens,
                        doc_tokens, vid):
        score = 0
        doc_len = coll["doc_lengths"][vid]
        avg_dl = coll["avg_doc_length"]
        doc_counter = Counter(doc_tokens)

        for token in query_tokens:
            if token not in doc_counter:
                continue

            tf = doc_counter[token]
            df = coll["df"].get(token, 0)
            n = coll["doc_count"]

            idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (
                1 - self.b + self.b * (doc_len / avg_dl))

            score += idf * (numerator / denominator)

        return score

    def _tokenize(self, text: str) -> list[str]:
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were',
            'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'and', 'or', 'but', 'not', 'this', 'that',
            'it', 'be', 'has', 'had', 'do', 'does',
            'what', 'which', 'how', 'when', 'where', 'who'
        }
        words = text.lower().split()
        cleaned = [w.strip('.,!?;:()[]"\'') for w in words]
        return [w for w in cleaned
                if w and len(w) > 1 and w not in stop_words]

    def _get(self, name: str) -> dict:
        if name not in self.collections:
            raise ValueError(f"BM25 collection not found: {name}")
        return self.collections[name]
