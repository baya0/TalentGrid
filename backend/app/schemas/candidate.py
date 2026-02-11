from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Dict, Any, Optional


class LanguageRecord(BaseModel):
    """Language proficiency recorrd"""

    name: str
    level: str | None = None


class EducationRecord(BaseModel):
    """Education record"""

    degree: str | None = None
    field: str | None = None
    institution: str | None = None
    start_date: str | None = None  # "from" in parser
    end_date: str | None = None  # "to" in parser


class ExperienceRecord(BaseModel):
    """Work experience record"""

    role: str | None = None
    organization: str | None = None
    start_date: str | None = None  # "from" in parser
    end_date: str | None = None  # "to" in parser
    description: str | None = None


class CandidateBase(BaseModel):
    """Base candidate fields"""

    name: str
    email: EmailStr | None = None
    phone: str | None = None
    title: str | None = None  # Current job title
    location: str | None = None
    years_experience: int = 0
    summary: str | None = None
    skills: List[str] = []


class CandidateCreate(CandidateBase):
    """Schema for creating a candidate"""

    languages: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    certifications: List[str] = []
    projects: List[str] = []
    links: Dict[str, str] = {}
    parsed_data: Dict[str, Any] | None = None
    source: str = "upload"


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate"""

    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    title: str | None = None
    location: str | None = None
    summary: str | None = None
    status: str | None = None
    match_percentage: int | None = None


class CandidateResponse(CandidateBase):
    """Schema for candidate response"""

    id: int
    languages: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    certifications: List[Any] = []
    projects: List[Any] = []
    links: Dict[str, Any] = {}
    quality_score: float | None = None
    match_percentage: int = 0
    ai_summary: str | None = None
    source: str | None = None
    status: str = "new"
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    """Schema for search queries"""

    query: str
    top_k: int = 10
    filters: Dict[str, Any] | None = None
