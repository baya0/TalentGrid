# app/routes/admin.py
"""
Admin routes for TalentGrid.
Includes system maintenance tasks like reindexing.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Track reindex status
_reindex_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "success": 0,
    "failed": 0,
    "message": "Idle"
}


def _do_reindex(db: Session):
    """Background task to reindex all candidates into ChromaDB."""
    global _reindex_status

    try:
        _reindex_status["running"] = True
        _reindex_status["message"] = "Starting reindex..."

        # Get all candidates
        candidates = db.query(Candidate).all()
        total = len(candidates)

        _reindex_status["total"] = total
        _reindex_status["progress"] = 0
        _reindex_status["success"] = 0
        _reindex_status["failed"] = 0

        if total == 0:
            _reindex_status["message"] = "No candidates to index"
            _reindex_status["running"] = False
            return

        # Initialize AI service
        from app.ai.service import AIService
        ai_service = AIService()

        for i, candidate in enumerate(candidates, 1):
            _reindex_status["progress"] = i
            _reindex_status["message"] = f"Indexing {i}/{total}: {candidate.name}"

            # Build CV data structure
            cv_data = {
                "name": candidate.name or "Unknown",
                "email": candidate.email or "",
                "phone": candidate.phone or "",
                "location": candidate.location or "",
                "title": candidate.title or "",
                "summary": candidate.summary or "",
                "skills": candidate.skills or [],
                "years_experience": candidate.years_experience or 0,
                "languages": candidate.languages or [],
                "experience": candidate.experience or [],
                "education": candidate.education or [],
                "certifications": candidate.certifications or [],
                "projects": candidate.projects or [],
            }

            try:
                result = ai_service.ingest_cv(cv_data, candidate_id=candidate.id)
                if result:
                    _reindex_status["success"] += 1
                else:
                    _reindex_status["failed"] += 1
            except Exception as e:
                logger.error(f"Failed to index {candidate.name}: {e}")
                _reindex_status["failed"] += 1

        _reindex_status["message"] = f"Complete! {_reindex_status['success']}/{total} indexed"
        _reindex_status["running"] = False

    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        _reindex_status["message"] = f"Error: {str(e)}"
        _reindex_status["running"] = False


@router.post("/reindex")
async def start_reindex(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start reindexing all candidates into ChromaDB vector store.

    This runs in the background - use GET /api/admin/reindex/status to check progress.

    Use this when:
    - After deployment to index existing candidates
    - If search results seem incomplete
    - After database restore
    """
    global _reindex_status

    if _reindex_status["running"]:
        raise HTTPException(
            status_code=409,
            detail="Reindex already in progress"
        )

    # Start background task
    background_tasks.add_task(_do_reindex, db)

    return {
        "message": "Reindex started",
        "status_url": "/api/admin/reindex/status"
    }


@router.get("/reindex/status")
async def get_reindex_status(
    current_user: User = Depends(get_current_user)
):
    """Get the current status of the reindex operation."""
    return _reindex_status


@router.get("/vector-store/stats")
async def get_vector_store_stats(
    current_user: User = Depends(get_current_user)
):
    """Get statistics about the ChromaDB vector store."""
    try:
        import chromadb

        client = chromadb.PersistentClient(path="./chroma_db")
        collections = client.list_collections()

        stats = {
            "collections": []
        }

        for coll in collections:
            stats["collections"].append({
                "name": coll.name,
                "document_count": coll.count()
            })

        return stats

    except Exception as e:
        return {"error": str(e)}
