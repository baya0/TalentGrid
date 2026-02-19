from app.ai.retrieval.query_parser import QueryParser
from app.ai.retrieval.hybrid_search import HybridSearch
from app.ai.storage.vector_store import VectorStore
from app.ai.ingestion.embedder import Embedder
import logging

logger = logging.getLogger(__name__)


class Retriever:

    def __init__(self):

        self.parser = QueryParser()
        self.store = VectorStore()
        self.embedder = Embedder()

        self.hybrid = HybridSearch(self.store)

    def retrieve(self, user_query: str, ui_filters: dict, top_k: int = 20):
        """
        Retrieve candidates WITHOUT ranking.

        Args:
            user_query: The search query text
            ui_filters: Filters from the UI (min_experience, max_experience, etc.)
            top_k: Number of final candidates needed. When filters are active,
                   we fetch a wider pool from ChromaDB because SQL post-filtering
                   (language, location) will reduce the count.
        """

        # 1️⃣ Parse
        parsed = self.parser.parse(user_query, ui_filters)

        clean_query = parsed["query"]
        filters = parsed["filters"]

        logger.info(
            f"[RETRIEVER] Query: '{clean_query}' | ChromaDB filters: {filters} | UI filters: {ui_filters}"
        )

        # 2️⃣ Embed
        query_vector = self.embedder.embed(clean_query)
        logger.info(f"[RETRIEVER] Embedding generated (dim={len(query_vector)})")

        # 3️⃣ Hybrid / Filtered Search
        self.hybrid.original_query = clean_query

        ranked = []
        docs = {}

        # When ChromaDB filters are active (experience range), SQL will further
        # filter by language/location. Fetch a wider pool so enough candidates
        # survive the full filter chain.
        has_sql_filters = bool(
            ui_filters and (ui_filters.get("languages") or ui_filters.get("location"))
        )
        fetch_k = max(top_k * 3, 60) if has_sql_filters else max(top_k, 20)

        # ----------------------------------
        # Step 1: Try filtered search first
        # ----------------------------------
        if filters:
            logger.info(
                f"[RETRIEVER] Filtered search: fetching {fetch_k} chunks from ChromaDB"
            )

            ranked, docs = self.hybrid.search(query_vector, filters=filters, k=fetch_k)

            logger.info(f"[RETRIEVER] Filtered search returned {len(ranked)} chunks")

        # ----------------------------------
        # Step 2: Fallback → full hybrid
        # ----------------------------------
        if not ranked:
            fallback_k = max(top_k, 20)
            logger.info(
                f"[RETRIEVER] No filtered results, fallback to unfiltered search (k={fallback_k})"
            )

            ranked, docs = self.hybrid.search(query_vector, filters=None, k=fallback_k)

            logger.info(f"[RETRIEVER] Unfiltered search returned {len(ranked)} chunks")

        # 4️⃣ Group by CV - Use MAX score (not sum) to avoid >100%
        results = {}

        for doc_id, score in ranked:
            cv_id = doc_id.split("_")[0]

            if cv_id not in results:
                results[cv_id] = {"score": 0, "chunks": [], "chunk_scores": []}

            # Track all chunk scores for this CV
            results[cv_id]["chunk_scores"].append(score)
            results[cv_id]["chunks"].append(docs[doc_id])

        # Calculate final score per CV: weighted combination of best + average
        # Pure MAX is bad because one lucky chunk match inflates the whole CV score
        # A real match should have MULTIPLE relevant chunks (skills + experience + title)
        for cv_id in results:
            chunk_scores = results[cv_id]["chunk_scores"]
            if not chunk_scores:
                results[cv_id]["score"] = 0
                continue

            best_score = max(chunk_scores)
            avg_score = sum(chunk_scores) / len(chunk_scores)

            # 70% best chunk + 30% average of all chunks
            # This rewards candidates who match across multiple sections
            results[cv_id]["score"] = 0.7 * best_score + 0.3 * avg_score

        # 5️⃣ Prepare candidates with normalized scores
        candidates = []

        for cv_id, data in results.items():
            text = " ".join(data["chunks"][:3])  # Limit text to top 3 chunks

            candidates.append(
                {
                    "id": cv_id,
                    "text": text,
                    "retrieval_score": data["score"],  # Now 0-1 range
                }
            )

        logger.info(
            f"[RETRIEVER] Grouped into {len(candidates)} unique CVs from {len(ranked)} chunks"
        )
        if candidates:
            top_scores = sorted(
                [c["retrieval_score"] for c in candidates], reverse=True
            )[:5]
            logger.info(
                f"[RETRIEVER] Top retrieval scores: {[round(s, 3) for s in top_scores]}"
            )

        return clean_query, candidates
