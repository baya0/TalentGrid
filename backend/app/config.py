# app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # CV Processing (Mistral OCR + LLM parsing)
    MISTRAL_API_KEY: str = ""
    GROQ_API_KEY: str = ""  # Primary LLM provider (free, 14,400 req/day)
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""  # Fallback LLM provider

    # RAG System (Embeddings + Ranking)
    HF_TOKEN: str = ""  # Hugging Face token for embeddings
    COHERE_API_KEY: str = ""  # For cross-encoder re-ranking
    LANGSMITH_API_KEY: str = ""  # LangSmith for tracing (optional)

    # ChromaDB path for vector storage
    CHROMA_DB_PATH: str = "./chroma_db"

    # Gmail OAuth (for CV import from email)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/import"

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
