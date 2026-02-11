# app/routes/gmail.py
"""
Gmail OAuth routes for importing CVs from email attachments.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from pathlib import Path
import tempfile

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.candidate import Candidate
from app.models.cv_file import CVFile
from app.services.auth_service import get_current_user
from app.ai import parse_cv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gmail", tags=["Gmail Import"])


# Request/Response Models
class OAuthUrlResponse(BaseModel):
    auth_url: str
    state: str


class TokenExchangeRequest(BaseModel):
    code: str
    state: str


class TokenResponse(BaseModel):
    success: bool
    message: str


class AttachmentInfo(BaseModel):
    filename: str
    attachment_id: str
    size: int
    mime_type: str


class EmailWithCVs(BaseModel):
    message_id: str
    subject: str
    from_email: str = ""
    date: str
    attachments: List[AttachmentInfo]


class ScanRequest(BaseModel):
    tokens: Dict
    max_results: int = 50
    days_back: int = 30


class ScanResponse(BaseModel):
    emails: List[EmailWithCVs]
    total_cvs: int


class ImportRequest(BaseModel):
    tokens: Dict
    message_id: str
    attachment_id: str
    filename: str


# In-memory token storage (per user session)
# In production, store encrypted in database
_user_tokens: Dict[int, Dict] = {}


@router.get("/auth", response_model=OAuthUrlResponse)
async def get_auth_url(current_user: User = Depends(get_current_user)):
    """
    Get Google OAuth URL to initiate Gmail authorization.
    Frontend should redirect user to this URL.
    """
    try:
        from app.services.gmail_service import get_oauth_url

        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gmail integration not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
            )

        auth_url, state = get_oauth_url(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        return OAuthUrlResponse(auth_url=auth_url, state=state)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to generate OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )


@router.post("/callback", response_model=TokenResponse)
async def exchange_token(
    request: TokenExchangeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Exchange authorization code for access tokens.
    Called by frontend after user completes OAuth flow.
    """
    try:
        from app.services.gmail_service import exchange_code_for_tokens

        tokens = exchange_code_for_tokens(
            code=request.code,
            state=request.state,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        # Store tokens for this user's session
        _user_tokens[current_user.id] = tokens

        return TokenResponse(success=True, message="Gmail connected successfully")

    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Gmail: {str(e)}"
        )


@router.get("/status")
async def get_connection_status(current_user: User = Depends(get_current_user)):
    """Check if user has connected Gmail."""
    connected = current_user.id in _user_tokens
    return {"connected": connected}


@router.post("/scan", response_model=ScanResponse)
async def scan_for_cvs(
    request: ScanRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Scan Gmail inbox for emails with CV attachments.
    Returns list of emails with their CV attachments.
    """
    try:
        from app.services.gmail_service import scan_emails_for_cvs

        # Use provided tokens or stored tokens
        tokens = request.tokens or _user_tokens.get(current_user.id)
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gmail not connected. Please authorize first."
            )

        emails = scan_emails_for_cvs(
            tokens=tokens,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            max_results=request.max_results,
            days_back=request.days_back
        )

        # Transform to response format
        email_responses = []
        total_cvs = 0
        for email in emails:
            attachments = [
                AttachmentInfo(
                    filename=att['filename'],
                    attachment_id=att['attachment_id'],
                    size=att['size'],
                    mime_type=att['mime_type']
                )
                for att in email['attachments']
            ]
            total_cvs += len(attachments)
            email_responses.append(EmailWithCVs(
                message_id=email['message_id'],
                subject=email['subject'],
                from_email=email['from'],
                date=email['date'],
                attachments=attachments
            ))

        return ScanResponse(emails=email_responses, total_cvs=total_cvs)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gmail scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scan emails: {str(e)}"
        )


@router.post("/import")
async def import_cv_from_gmail(
    request: ImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import a specific CV attachment from Gmail.
    Downloads the attachment and processes it through the CV parser.
    """
    try:
        from app.services.gmail_service import download_attachment

        # Use provided tokens or stored tokens
        tokens = request.tokens or _user_tokens.get(current_user.id)
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gmail not connected. Please authorize first."
            )

        # Download attachment
        file_data = download_attachment(
            tokens=tokens,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            message_id=request.message_id,
            attachment_id=request.attachment_id
        )

        # Save to temp file for parsing
        file_ext = Path(request.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name

        try:
            # Parse CV using existing parser (Mistral OCR + Gemini)
            parsed_data = await parse_cv(tmp_path)

            # Create candidate FIRST (before CVFile, due to NOT NULL constraint)
            new_candidate = Candidate(
                name=parsed_data.get("name", "Unknown"),
                email=parsed_data.get("email"),
                phone=parsed_data.get("phone"),
                title=parsed_data.get("title"),
                location=parsed_data.get("location"),
                years_experience=parsed_data.get("years_experience", 0),
                summary=parsed_data.get("summary"),
                skills=parsed_data.get("skills", []),
                languages=parsed_data.get("languages", []),
                education=parsed_data.get("education", []),
                experience=parsed_data.get("experience", []),
                certifications=parsed_data.get("certifications", []),
                projects=parsed_data.get("projects", []),
                links=parsed_data.get("links", {}),
                parsed_data=parsed_data,
                source="gmail"  # Mark as imported from Gmail
            )

            db.add(new_candidate)
            db.commit()
            db.refresh(new_candidate)

            # NOW create CV file record with candidate_id
            cv_file = CVFile(
                candidate_id=new_candidate.id,
                filename=request.filename,
                file_path=tmp_path,
                file_type=file_ext.strip("."),
                file_size=len(file_data),
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
                # Don't fail the import if AI ingestion fails
                logger.warning(f"AI ingestion failed (non-critical): {ai_error}")

            logger.info(f"Successfully imported CV from Gmail: {new_candidate.name}")

            return {
                "success": True,
                "candidate_id": new_candidate.id,
                "name": new_candidate.name,
                "email": new_candidate.email,
                "title": new_candidate.title
            }

        except Exception as e:
            logger.error(f"CV parsing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse CV: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gmail import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import CV: {str(e)}"
        )


@router.delete("/disconnect")
async def disconnect_gmail(current_user: User = Depends(get_current_user)):
    """Disconnect Gmail (remove stored tokens)."""
    if current_user.id in _user_tokens:
        del _user_tokens[current_user.id]
    return {"success": True, "message": "Gmail disconnected"}
