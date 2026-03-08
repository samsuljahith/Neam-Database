from config import settings

class Explainer:
    """Generates human-readable explanations for search results."""

    def __init__(self):
        self.high_threshold = 0.65
        self.medium_threshold = 0.4

    def explain(self, query: str, result_text: str,
                score: float) -> dict:
        """Generate explanation for a single search result."""
        confidence = self._get_confidence(score)
        matching = self._find_matching_concepts(query, result_text)
        coverage = self._calculate_coverage(query, matching)

        return {
            "confidence": confidence,
            "score_interpretation": self._interpret_score(score),
            "matching_concepts": matching,
            "query_coverage": round(coverage, 2),
            "why": self._generate_why(
                confidence, matching, query, result_text)
        }

    def _get_confidence(self, score: float) -> str:
        if score >= self.high_threshold:
            return "high"
        elif score >= self.medium_threshold:
            return "medium"
        return "low"

    def _interpret_score(self, score: float) -> str:
        if score >= self.high_threshold:
            return "Strong semantic match"
        elif score >= self.medium_threshold:
            return "Moderately related content"
        return "Weak match — may not be relevant"

    def _find_matching_concepts(self, query: str,
                                 text: str) -> list[str]:
        """Find overlapping meaningful words."""
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were',
            'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'and', 'or', 'but', 'not', 'this', 'that',
            'it', 'be', 'has', 'had', 'do', 'does',
            'what', 'which', 'how', 'when', 'where', 'who'
        }

        query_words = set(query.lower().split()) - stop_words
        text_words = set(text.lower().split()) - stop_words

        # Clean punctuation
        query_words = {w.strip('.,!?;:') for w in query_words}
        text_words = {w.strip('.,!?;:') for w in text_words}

        return sorted(query_words & text_words)

    def _calculate_coverage(self, query: str,
                            matching: list[str]) -> float:
        """What fraction of query concepts appear in result."""
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were',
            'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'and', 'or', 'but', 'not', 'this', 'that',
            'it', 'be', 'has', 'had', 'do', 'does',
            'what', 'which', 'how', 'when', 'where', 'who'
        }
        query_words = set(query.lower().split()) - stop_words
        query_words = {w.strip('.,!?;:') for w in query_words}

        if not query_words:
            return 0.0
        return len(matching) / len(query_words)

    def _generate_why(self, confidence, matching,
                      query, text) -> str:
        """Human-readable reason for the match."""
        if confidence == "high" and matching:
            return (f"Strong match. Shared concepts: "
                    f"{', '.join(matching)}. Both texts are "
                    f"semantically aligned.")
        elif confidence == "high":
            return ("Strong semantic similarity even without "
                    "exact word overlap — meaning is closely "
                    "related.")
        elif confidence == "medium" and matching:
            return (f"Moderate match. Shared concepts: "
                    f"{', '.join(matching)}. Content is "
                    f"related but not a direct answer.")
        elif confidence == "medium":
            return ("Some semantic relationship detected "
                    "but no direct word overlap.")
        else:
            return ("Weak match. This result may not be "
                    "relevant to your query.")
