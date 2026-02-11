# app/routes/search.py
"""
Search routes for TalentGrid.

Uses RAG (Retrieval Augmented Generation) for semantic search:
- Hybrid search (semantic + keyword)
- Cross-encoder re-ranking
- Database lookup for full candidate data
- Filtering by experience, skills, location
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchFilters(BaseModel):
    """Search filters model - uses existing database fields."""
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    languages: Optional[List[str]] = None
    location: Optional[str] = None


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    top_k: int = 10
    filters: Optional[SearchFilters] = None
    use_reranking: bool = True


class SearchResult(BaseModel):
    """Search result model."""
    id: int
    name: str
    email: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    years_experience: int = 0
    score: float = 0.0
    match_reason: Optional[str] = None

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    total_results: int
    candidates: List[SearchResult]


def apply_filters(query, filters: SearchFilters):
    """Apply filters to a SQLAlchemy query."""
    if not filters:
        return query

    conditions = []

    # Experience filter
    if filters.min_experience is not None:
        conditions.append(Candidate.years_experience >= filters.min_experience)
    if filters.max_experience is not None:
        conditions.append(Candidate.years_experience <= filters.max_experience)

    # Location filter (partial match)
    if filters.location:
        conditions.append(Candidate.location.ilike(f"%{filters.location}%"))

    # Languages filter (candidate must speak at least one of the languages)
    # Languages are stored as JSONB array: [{"name": "English", "level": "Native"}, ...]
    if filters.languages and len(filters.languages) > 0:
        from sqlalchemy import cast, String
        lang_conditions = []
        for lang in filters.languages:
            # Search in the JSONB array for language name (case-insensitive)
            lang_conditions.append(
                cast(Candidate.languages, String).ilike(f'%{lang}%')
            )
        conditions.append(or_(*lang_conditions))

    if conditions:
        query = query.filter(and_(*conditions))

    return query


@router.post("/", response_model=SearchResponse)
async def search_candidates(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Semantic search for candidates using RAG.

    Features:
    - Hybrid search (semantic embeddings + BM25 keyword matching)
    - Optional cross-encoder re-ranking (requires COHERE_API_KEY)
    - Filtering by experience, skills, location
    """
    try:
        from app.ai.service import get_ai_service
        ai_service = get_ai_service()

        logger.info(f"[SEARCH] === New search: '{request.query}' ===")
        logger.info(f"[SEARCH] Filters: {request.filters.model_dump() if request.filters else 'none'}")
        logger.info(f"[SEARCH] Path: RAG (semantic + hybrid)")

        # Perform semantic search — request extra results because SQL
        # post-filtering (language, location) will reduce the pool
        rag_results = ai_service.search(
            query=request.query,
            filters=request.filters.model_dump() if request.filters else None,
            top_k=request.top_k * 3,
            use_reranking=request.use_reranking
        )

        logger.info(f"[SEARCH] RAG returned {len(rag_results) if rag_results else 0} candidates")

        if rag_results:
            results = []
            seen_ids = set()

            # SQL verification layer: experience is already filtered at ChromaDB
            # level, but language/location can only be checked here
            base_query = db.query(Candidate)
            if request.filters:
                base_query = apply_filters(base_query, request.filters)

            for rag_result in rag_results:
                score = rag_result.get("score", rag_result.get("retrieval_score", 0))
                text = rag_result.get("text", "")
                candidate_id = rag_result.get("candidate_id")

                # Method 1: Direct lookup using candidate_id (reliable)
                if candidate_id and candidate_id not in seen_ids:
                    candidate = base_query.filter(Candidate.id == candidate_id).first()
                    if candidate:
                        seen_ids.add(candidate.id)
                        results.append(SearchResult(
                            id=candidate.id,
                            name=candidate.name,
                            email=candidate.email,
                            title=candidate.title,
                            location=candidate.location,
                            skills=candidate.skills or [],
                            years_experience=candidate.years_experience or 0,
                            score=round(score, 3),
                            match_reason=text[:200] if text else None
                        ))

                        if len(results) >= request.top_k:
                            break
                        continue

                # Method 2: Fallback to name matching for legacy data without candidate_id
                if not candidate_id:
                    filtered_candidates = base_query.all()
                    for candidate in filtered_candidates:
                        if candidate.id in seen_ids:
                            continue

                        if candidate.name and candidate.name.lower() in text.lower():
                            seen_ids.add(candidate.id)
                            results.append(SearchResult(
                                id=candidate.id,
                                name=candidate.name,
                                email=candidate.email,
                                title=candidate.title,
                                location=candidate.location,
                                skills=candidate.skills or [],
                                years_experience=candidate.years_experience or 0,
                                score=round(score, 3),
                                match_reason=text[:200] if text else None
                            ))

                            if len(results) >= request.top_k:
                                break

                if len(results) >= request.top_k:
                    break

            # Return RAG results (even if empty — that's an honest answer)
            logger.info(f"[SEARCH] Final: {len(results)} candidates passed SQL filters (from {len(rag_results)} RAG results)")
            if results:
                logger.info(f"[SEARCH] Top result: {results[0].name} (score={results[0].score})")
            return SearchResponse(
                query=request.query,
                total_results=len(results),
                candidates=results
            )

        # RAG returned nothing at all — use text-based fallback
        logger.info("[SEARCH] RAG returned 0 results, falling back to text search")
        return await _fallback_search(request, db)

    except Exception as e:
        # RAG system error — use text-based fallback as safety net
        logger.error(f"[SEARCH] RAG system error: {e} — falling back to text search")
        return await _fallback_search(request, db)


async def _fallback_search(request: SearchRequest, db: Session) -> SearchResponse:
    """
    Text-based fallback — only used when the RAG system is unavailable.

    Searches by query text across name, title, summary, and skills
    with case-insensitive matching. Returns empty results if nothing
    matches rather than returning unrelated candidates.
    """
    logger.info(f"[SEARCH] === FALLBACK: text-based search (RAG unavailable) ===")

    query_text = request.query.lower()

    base_query = db.query(Candidate)

    # Apply filters
    if request.filters:
        base_query = apply_filters(base_query, request.filters)

    # Try full query text search (case-insensitive for all fields including skills)
    candidates = base_query.filter(
        or_(
            Candidate.name.ilike(f"%{query_text}%"),
            Candidate.title.ilike(f"%{query_text}%"),
            Candidate.summary.ilike(f"%{query_text}%"),
            func.array_to_string(Candidate.skills, ',').ilike(f"%{query_text}%")
        )
    ).limit(request.top_k).all()

    # If no results, try matching individual keywords
    if not candidates:
        keywords = query_text.split()
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(Candidate.name.ilike(f"%{keyword}%"))
                keyword_conditions.append(Candidate.title.ilike(f"%{keyword}%"))
                keyword_conditions.append(Candidate.summary.ilike(f"%{keyword}%"))
                keyword_conditions.append(func.array_to_string(Candidate.skills, ',').ilike(f"%{keyword}%"))
            candidates = base_query.filter(or_(*keyword_conditions)).limit(request.top_k).all()

    results = [
        SearchResult(
            id=c.id,
            name=c.name,
            email=c.email,
            title=c.title,
            location=c.location,
            skills=c.skills or [],
            years_experience=c.years_experience or 0,
            score=0.5,
            match_reason="Text search (RAG unavailable)"
        )
        for c in candidates
    ]

    return SearchResponse(
        query=request.query,
        total_results=len(results),
        candidates=results
    )


@router.get("/all")
async def get_all_candidates_for_search(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all candidates without search query.
    Useful for listing all candidates or when search is empty.
    """
    candidates = db.query(Candidate).limit(limit).all()

    results = [
        SearchResult(
            id=c.id,
            name=c.name,
            email=c.email,
            title=c.title,
            location=c.location,
            skills=c.skills or [],
            years_experience=c.years_experience or 0,
            score=1.0,
            match_reason="All candidates"
        )
        for c in candidates
    ]

    return SearchResponse(
        query="",
        total_results=len(results),
        candidates=results
    )


@router.get("/health")
async def search_health():
    """Check if RAG search system is healthy."""
    try:
        from app.ai.service import get_ai_service
        ai_service = get_ai_service()

        status = {
            "rag_available": True,
            "embedder": "ready",
            "vector_store": "ready",
            "reranker": "ready" if ai_service.ranker and ai_service.ranker.available else "not configured"
        }

        return {"status": "healthy", "components": status}

    except Exception as e:
        return {"status": "degraded", "error": str(e)}
