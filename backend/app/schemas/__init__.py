# app/schemas/__init__.py
from app.schemas.auth import UserRegister, UserLogin, Token, TokenData
from app.schemas.user import UserResponse, UserCreate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    SearchQuery,
    EducationRecord,
    ExperienceRecord,
    LanguageRecord
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenData",
    "UserResponse",
    "UserCreate",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "SearchQuery",
    "EducationRecord",
    "ExperienceRecord",
    "LanguageRecord",
]
