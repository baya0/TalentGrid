# app/ai/ranking/cross_encoder.py
"""
Cross-encoder re-ranking using Cohere API.
Optional - if no API key, ranking is skipped.
"""
import os
import logging

logger = logging.getLogger(__name__)

# Global client instance (lazy loaded)
_client = None
_available = None


def _get_client():
    """Lazy load the Cohere client."""
    global _client, _available

    # Always re-check if previously unavailable (key might have been added)
    if _available is None or _available is False:
        from app.config import settings

        api_key = settings.COHERE_API_KEY
        if not api_key:
            logger.warning(
                "COHERE_API_KEY not set. Cross-encoder ranking will be skipped."
            )
            _available = False
            return None

        try:
            import cohere

            _client = cohere.ClientV2(api_key)
            _available = True
            logger.info("Cohere client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
            _available = False
            return None

    return _client if _available else None


class CrossEncoder:
    """
    Cross-encoder re-ranker using Cohere API.
    If API key is not available, returns candidates unchanged.
    """

    def __init__(self):
        """Initialize the CrossEncoder (client loaded lazily)."""
        self._client = None

    @property
    def client(self):
        """Get the client, loading it if necessary."""
        if self._client is None:
            self._client = _get_client()
        return self._client

    @property
    def available(self):
        """Check if cross-encoder is available."""
        return self.client is not None

    def rank(self, query: str, candidates: list) -> list:
        """
        Rank candidates based on their relevance to the query.

        Args:
            query (str): The search query.
            candidates (list[dict]): A list of candidates with "text" field.

        Returns:
            list[dict]: The ranked candidates with scores.
        """
        if not candidates:
            return candidates

        # If Cohere is not available, return as-is with retrieval scores
        if not self.available:
            logger.debug("Cross-encoder not available, using retrieval scores only")
            for candidate in candidates:
                if "score" not in candidate:
                    candidate["score"] = candidate.get("retrieval_score", 0)
            return sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)

        try:
            # Call the rerank endpoint
            response = self.client.rerank(
                model="rerank-v3.5",
                query=query,
                documents=[candidate["text"] for candidate in candidates],
                top_n=len(candidates),
            )

            # Attach scores to candidates
            for result in response.results:
                idx = result.index
                candidates[idx]["score"] = result.relevance_score

            # Sort candidates by score in descending order
            ranked_candidates = sorted(
                candidates, key=lambda x: x.get("score", 0), reverse=True
            )
            return ranked_candidates

        except Exception as e:
            logger.error(f"Cohere rerank failed: {e}")
            # Fallback to retrieval scores
            for candidate in candidates:
                if "score" not in candidate:
                    candidate["score"] = candidate.get("retrieval_score", 0)
            return sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
