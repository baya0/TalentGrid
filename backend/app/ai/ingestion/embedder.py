# app/ai/ingestion/embedder.py
"""
Embedder module for converting text to vectors.
Uses SentenceTransformer with lazy initialization.
"""
import os
import logging

logger = logging.getLogger(__name__)

# Default model - all-mpnet-base-v2 provides better semantic understanding
# than all-MiniLM-L6-v2 (768 dimensions vs 384, deeper architecture)
DEFAULT_MODEL = "all-mpnet-base-v2"

# Global model instance (lazy loaded)
_model = None
_model_name = None


def _get_model(model_name=None):
    """Lazy load the SentenceTransformer model."""
    global _model, _model_name

    target_model = model_name or DEFAULT_MODEL

    # Reload if model name changed
    if _model is None or _model_name != target_model:
        try:
            from sentence_transformers import SentenceTransformer

            # Cache directory for models
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "ai_recruiter_models")
            os.makedirs(cache_dir, exist_ok=True)

            # Load the model (public HuggingFace models, no token needed)
            _model = SentenceTransformer(target_model, cache_folder=cache_dir)
            _model_name = target_model
            logger.info(f"SentenceTransformer model '{target_model}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            raise
    return _model


class Embedder:
    """
    Embedder class for converting text to vectors.
    Uses all-mpnet-base-v2 model from SentenceTransformers (768 dimensions).
    """

    def __init__(self, model_name=None):
        """Initialize embedder (model loaded lazily on first use)."""
        self._model = None
        self.model_name = model_name or DEFAULT_MODEL

    @property
    def model(self):
        """Get the model, loading it if necessary."""
        if self._model is None:
            self._model = _get_model(self.model_name)
        return self._model

    def embed(self, text: str) -> list:
        """
        Convert text to vector representation.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        vector = self.model.encode(text)
        return vector.tolist()

    def embed_batch(self, texts: list) -> list:
        """
        Convert multiple texts to vectors.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        vectors = self.model.encode(texts)
        return [v.tolist() for v in vectors]
