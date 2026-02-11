# app/ai/service.py
"""
Unified AI Service for TalentGrid.

Provides a clean interface for:
- CV ingestion (parsing, chunking, embedding, storage)
- Semantic search with hybrid retrieval
- Re-ranking with cross-encoder
- Quality evaluation
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy-loaded service instances
_ingestion_pipeline = None
_retriever = None
_ranker = None


def get_ingestion_pipeline():
    """Get the ingestion pipeline (lazy loaded)."""
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        try:
            from app.ai.ingestion.pipeline import IngestionPipeline
            _ingestion_pipeline = IngestionPipeline()
            logger.info("Ingestion pipeline initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ingestion pipeline: {e}")
            raise
    return _ingestion_pipeline


def get_retriever():
    """Get the retriever (lazy loaded)."""
    global _retriever
    if _retriever is None:
        try:
            from app.ai.retrieval.retriever import Retriever
            _retriever = Retriever()
            logger.info("Retriever initialized")
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            raise
    return _retriever


def get_ranker():
    """Get the cross-encoder ranker (lazy loaded)."""
    global _ranker
    if _ranker is None:
        try:
            from app.ai.ranking.cross_encoder import CrossEncoder
            _ranker = CrossEncoder()
            logger.info("Cross-encoder ranker initialized")
        except Exception as e:
            logger.warning(f"Cross-encoder not available: {e}")
            _ranker = None
    return _ranker


class AIService:
    """
    Unified AI service for TalentGrid.

    Provides methods for:
    - Ingesting parsed CVs into the vector store
    - Searching candidates using RAG
    - Re-ranking results
    """

    def __init__(self):
        """Initialize AI service (components lazy loaded on first use)."""
        self._pipeline = None
        self._retriever = None
        self._ranker = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = get_ingestion_pipeline()
        return self._pipeline

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = get_retriever()
        return self._retriever

    @property
    def ranker(self):
        if self._ranker is None:
            self._ranker = get_ranker()
        return self._ranker

    def ingest_cv(self, cv_data: Dict, candidate_id: Optional[int] = None) -> bool:
        """
        Ingest a parsed CV into the vector store.

        Args:
            cv_data: Parsed CV data (from Mistral OCR + Gemini)
            candidate_id: Database candidate ID for direct lookup in search

        Returns:
            True if successful, False otherwise
        """
        try:
            if candidate_id is not None:
                # Use direct ingestion with candidate_id in metadata
                # This allows search to directly map results to database records
                self._ingest_with_candidate_id(cv_data, candidate_id)
            else:
                # Fallback to standard pipeline (backward compatible)
                self.pipeline.ingest_one(cv_data)

            logger.info(f"CV ingested: {cv_data.get('name', 'Unknown')} (candidate_id={candidate_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest CV: {e}")
            return False

    def _ingest_with_candidate_id(self, cv_data: Dict, candidate_id: int) -> None:
        """
        Ingest CV with candidate_id injected into chunk metadata.

        This wraps the team's chunker/embedder without modifying their code,
        adding candidate_id to enable direct database lookup in search.
        """
        from app.ai.ingestion.chunker import CVChunker
        from app.ai.ingestion.embedder import Embedder
        from app.ai.storage.vector_store import VectorStore

        chunker = CVChunker()
        embedder = Embedder()
        store = VectorStore()

        # Get chunks from team's chunker
        chunks = chunker.chunk(cv_data)

        for chunk in chunks:
            # Inject candidate_id into metadata (without modifying chunker code)
            chunk["metadata"]["candidate_id"] = candidate_id

            # Clean metadata (replace None with empty string)
            metadata_clean = {k: ("" if v is None else v) for k, v in chunk["metadata"].items()}

            # Embed and store
            vector = embedder.embed(chunk["text"])
            store.add(
                ids=[chunk["id"]],
                documents=[chunk["text"]],
                embeddings=[vector],
                metadatas=[metadata_clean]
            )

    def ingest_many_cvs(self, cv_list: List[Dict]) -> int:
        """
        Ingest multiple CVs into the vector store.

        Args:
            cv_list: List of parsed CV data

        Returns:
            Number of CVs successfully ingested
        """
        success_count = 0
        for cv_data in cv_list:
            if self.ingest_cv(cv_data):
                success_count += 1
        return success_count

    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: int = 10,
        use_reranking: bool = True
    ) -> List[Dict]:
        """
        Search for candidates using semantic search.

        Args:
            query: Natural language search query
            filters: Optional filters (e.g., {"experience_years": {"$gte": 3}})
            top_k: Number of results to return
            use_reranking: Whether to use cross-encoder re-ranking

        Returns:
            List of candidate results with scores and candidate_ids
        """
        try:
            # Retrieve candidates - pass top_k so retriever can fetch a
            # wider pool from ChromaDB when SQL post-filtering is needed
            clean_query, candidates = self.retriever.retrieve(
                user_query=query,
                ui_filters=filters or {},
                top_k=top_k
            )

            if not candidates:
                logger.info(f"[AI_SERVICE] No candidates found for query: {query}")
                return []

            logger.info(f"[AI_SERVICE] Retriever returned {len(candidates)} candidates")

            # Optionally re-rank
            if use_reranking and self.ranker and self.ranker.available:
                logger.info(f"[AI_SERVICE] Re-ranking with Cohere cross-encoder...")
                candidates = self.ranker.rank(clean_query, candidates)
                logger.info(f"[AI_SERVICE] Re-ranking complete")
            else:
                reason = "disabled" if not use_reranking else "Cohere unavailable"
                logger.info(f"[AI_SERVICE] Skipping re-ranking ({reason}), using retrieval scores")
                candidates = sorted(
                    candidates,
                    key=lambda x: x.get("retrieval_score", 0),
                    reverse=True
                )

            # Enrich candidates with candidate_id from vector store metadata
            candidates = self._enrich_with_candidate_ids(candidates[:top_k])
            enriched = sum(1 for c in candidates if c.get("candidate_id"))
            logger.info(f"[AI_SERVICE] Enriched {enriched}/{len(candidates)} candidates with DB IDs")

            return candidates

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _enrich_with_candidate_ids(self, candidates: List[Dict]) -> List[Dict]:
        """
        Look up candidate_id from vector store metadata for each result.

        This enables direct database lookup instead of unreliable name matching.
        """
        from app.ai.storage.vector_store import VectorStore

        try:
            store = VectorStore()

            for candidate in candidates:
                cv_id = candidate.get("id")  # This is the chunk UUID prefix
                if not cv_id:
                    continue

                # Query the vector store for any chunk from this CV to get metadata
                # Use the profile chunk as it's always present
                try:
                    result = store.collection.get(
                        ids=[f"{cv_id}_profile"],
                        include=["metadatas"]
                    )

                    if result and result.get("metadatas") and len(result["metadatas"]) > 0:
                        metadata = result["metadatas"][0]
                        db_candidate_id = metadata.get("candidate_id")
                        if db_candidate_id:
                            candidate["candidate_id"] = int(db_candidate_id)
                except Exception:
                    # Try skills chunk as fallback
                    try:
                        result = store.collection.get(
                            ids=[f"{cv_id}_skills"],
                            include=["metadatas"]
                        )
                        if result and result.get("metadatas") and len(result["metadatas"]) > 0:
                            metadata = result["metadatas"][0]
                            db_candidate_id = metadata.get("candidate_id")
                            if db_candidate_id:
                                candidate["candidate_id"] = int(db_candidate_id)
                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"Failed to enrich with candidate_ids: {e}")

        return candidates

    def get_candidate_by_cv_id(self, cv_id: str) -> Optional[Dict]:
        """
        Get candidate data by CV ID from the vector store.

        Args:
            cv_id: The CV ID

        Returns:
            Candidate data or None
        """
        # This would need to be implemented based on how data is stored
        # For now, return None
        return None

    def clear_vector_store(self) -> None:
        """
        Clear the vector store. Required when changing embedding models
        due to dimension changes.
        """
        from app.ai.storage.vector_store import VectorStore
        store = VectorStore()
        store.clear()
        logger.info("Vector store cleared")


# Singleton instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get the singleton AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
