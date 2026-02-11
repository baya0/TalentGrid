# app/models/cv_file.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class CVFile(Base):
    __tablename__ = "cv_files"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # "pdf", "docx"
    file_size = Column(Integer)  # Size in bytes
    upload_status = Column(String(50), default="pending")  # "pending", "processed", "failed"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
