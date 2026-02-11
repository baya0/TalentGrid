# app/models/__init__.py
from app.models.user import User
from app.models.candidate import Candidate
from app.models.cv_file import CVFile

__all__ = ["User", "Candidate", "CVFile"]
