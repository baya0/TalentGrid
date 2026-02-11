# app/models/candidate.py
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ARRAY, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info (matches test3.py schema)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    title = Column(String(255), index=True)  # Current job title
    location = Column(String(255))
    years_experience = Column(Integer, default=0)  # experience_years from parser
    summary = Column(Text)  # CV summary/objective

    # Skills as PostgreSQL ARRAY
    skills = Column(ARRAY(String), default=[])

    # Complex fields as JSONB (matches test3.py schema)
    languages = Column(JSONB, default=[])  # [{"name": "English", "level": "Native"}]
    education = Column(JSONB, default=[])  # [{"degree": "", "field": "", "institution": "", "from": "", "to": ""}]
    experience = Column(JSONB, default=[])  # [{"role": "", "organization": "", "from": "", "to": "", "description": ""}]
    certifications = Column(JSONB, default=[])  # List of certifications
    projects = Column(JSONB, default=[])  # projects_or_work from parser
    links = Column(JSONB, default={})  # {"linkedin": "url", "github": "url"}

    # Full parsed data storage
    parsed_data = Column(JSONB)  # Complete parsed CV data for reference

    # AI/RAG fields
    quality_score = Column(Numeric(3, 2))  # 0.00 to 10.00
    match_percentage = Column(Integer, default=0)
    ai_summary = Column(Text)

    # Metadata
    source = Column(String(100))  # "upload", "import", etc.
    status = Column(String(50), default="new")  # "new", "reviewed", "contacted"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
