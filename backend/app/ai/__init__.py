# app/ai/__init__.py
"""
TalentGrid AI Module

Provides:
- CV parsing (Mistral OCR + Gemini)
- Semantic search with hybrid retrieval
- Re-ranking with cross-encoder
- Quality evaluation
"""

# Main entry points
from app.ai.ingestion.parser import parse_cv
from app.ai.service import get_ai_service, AIService

__all__ = ["parse_cv", "get_ai_service", "AIService"]
