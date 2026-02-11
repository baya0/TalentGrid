"""
CV Ingestion Module

Provides CV parsing and ingestion into the vector store.
"""

from app.ai.ingestion.parser import (
    parse_cv,
    mistral_ocr_return,
    gemini_structured_cv_return,
)

__all__ = ["parse_cv", "mistral_ocr_return", "gemini_structured_cv_return"]
