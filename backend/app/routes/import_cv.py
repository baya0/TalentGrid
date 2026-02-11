# app/routes/import_cv.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import os
from pathlib import Path
import logging

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.models.cv_file import CVFile
from app.services.auth_service import get_current_user
from app.ai import parse_cv
from app.schemas.candidate import CandidateResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["Import"])

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/cv", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse a CV file (PDF or DOCX)

    Flow:
    1. Save file to disk
    2. Call CV parser (Mistral OCR + Gemini)
    3. Create candidate in database
    4. Track the CV file
    5. Return parsed candidate data
    """

    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save file to disk
    file_path = UPLOAD_DIR / f"{current_user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    file_size = len(content)

    try:
        # Parse CV using Mistral OCR + Gemini
        parsed_data = await parse_cv(str(file_path))

        # Create candidate FIRST (before CVFile, due to NOT NULL constraint)
        new_candidate = Candidate(
            # Basic info
            name=parsed_data.get("name", "Unknown"),
            email=parsed_data.get("email"),
            phone=parsed_data.get("phone"),
            title=parsed_data.get("title"),
            location=parsed_data.get("location"),
            years_experience=parsed_data.get("years_experience", 0),
            summary=parsed_data.get("summary"),

            # Arrays and complex fields
            skills=parsed_data.get("skills", []),
            languages=parsed_data.get("languages", []),
            education=parsed_data.get("education", []),
            experience=parsed_data.get("experience", []),
            certifications=parsed_data.get("certifications", []),
            projects=parsed_data.get("projects", []),
            links=parsed_data.get("links", {}),

            # Full parsed data for reference
            parsed_data=parsed_data,
            source="upload"
        )

        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        # Now create the CV file record (after candidate exists)
        cv_file = CVFile(
            candidate_id=new_candidate.id,
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_ext.strip("."),
            file_size=file_size,
            upload_status="processed"
        )
        db.add(cv_file)
        db.commit()

        # Ingest into vector store for RAG search (async, non-blocking)
        try:
            from app.ai.service import get_ai_service
            ai_service = get_ai_service()
            # Pass candidate_id for direct database lookup in search
            ai_service.ingest_cv(parsed_data, candidate_id=new_candidate.id)
            logger.info(f"CV ingested into vector store: {new_candidate.name}")
        except Exception as ai_error:
            # Don't fail the upload if AI ingestion fails
            logger.warning(f"AI ingestion failed (non-critical): {ai_error}")

        logger.info(f"Successfully parsed CV for candidate: {new_candidate.name}")

        return new_candidate

    except Exception as e:
        # Clean up the uploaded file on failure
        if file_path.exists():
            try:
                os.remove(file_path)
            except:
                pass

        logger.error(f"CV parsing failed: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV parsing failed: {str(e)}"
        )
