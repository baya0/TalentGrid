import re
import math
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class HybridSearch:
    """
    Hybrid search combining semantic (vector) and keyword (BM25) search.

    Dynamic weights based on query type:
    - Short skill queries (1-2 words like "flutter", "react"): 80% keyword, 20% semantic
    - Job descriptions (3+ words): 60% semantic, 40% keyword

    Features:
    - Title boosting: Candidates with matching job titles rank higher
    - Synonym expansion: Common tech term variations are matched
    """

    # Common English stop words to ignore in keyword matching
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'that', 'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'what', 'which', 'who', 'whom', 'where', 'when', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'also', 'now', 'skills', 'experience',
        'years', 'work', 'working', 'job', 'position', 'role', 'level',
        'looking', 'seeking', 'required', 'requirements', 'preferred'
    }

    # Common tech skills - exact matches should be boosted heavily
    TECH_SKILLS = {
        'flutter', 'dart', 'react', 'angular', 'vue', 'javascript', 'typescript',
        'python', 'java', 'kotlin', 'swift', 'go', 'rust', 'ruby', 'php',
        'node', 'nodejs', 'express', 'django', 'flask', 'spring', 'rails',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'react native', 'ios', 'android', 'mobile', 'frontend', 'backend',
        'fullstack', 'devops', 'mlops', 'machine learning', 'ml', 'ai',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit',
        'html', 'css', 'sass', 'tailwind', 'bootstrap',
        'git', 'agile', 'scrum', 'jira', 'figma', 'sketch'
    }

    # Synonym mappings for tech terms - bidirectional matching
    SYNONYMS = {
        'react': ['reactjs', 'react.js'],
        'reactjs': ['react', 'react.js'],
        'vue': ['vuejs', 'vue.js'],
        'vuejs': ['vue', 'vue.js'],
        'angular': ['angularjs', 'angular.js'],
        'node': ['nodejs', 'node.js'],
        'nodejs': ['node', 'node.js'],
        'javascript': ['js', 'ecmascript'],
        'js': ['javascript', 'ecmascript'],
        'typescript': ['ts'],
        'ts': ['typescript'],
        'python': ['py'],
        'py': ['python'],
        'golang': ['go'],
        'go': ['golang'],
        'kubernetes': ['k8s'],
        'k8s': ['kubernetes'],
        'postgresql': ['postgres', 'psql'],
        'postgres': ['postgresql', 'psql'],
        'mongodb': ['mongo'],
        'mongo': ['mongodb'],
        'elasticsearch': ['elastic', 'es'],
        'machine learning': ['ml', 'machinelearning'],
        'ml': ['machine learning', 'machinelearning'],
        'artificial intelligence': ['ai'],
        'ai': ['artificial intelligence'],
        'frontend': ['front-end', 'front end'],
        'backend': ['back-end', 'back end'],
        'fullstack': ['full-stack', 'full stack'],
        'devops': ['dev-ops', 'dev ops'],
        'react native': ['reactnative', 'rn'],
        'nextjs': ['next.js', 'next'],
        'nuxtjs': ['nuxt.js', 'nuxt'],
    }

    # Job title patterns for boosting
    TITLE_PATTERNS = {
        'developer': ['engineer', 'dev', 'programmer', 'coder'],
        'engineer': ['developer', 'dev'],
        'senior': ['sr', 'sr.', 'lead', 'principal'],
        'junior': ['jr', 'jr.', 'entry'],
        'frontend': ['front-end', 'front end', 'ui'],
        'backend': ['back-end', 'back end', 'server'],
        'fullstack': ['full-stack', 'full stack'],
        'data scientist': ['data science', 'ml engineer'],
        'devops': ['sre', 'site reliability', 'platform engineer'],
        'mobile': ['ios', 'android', 'app developer'],
    }

    def __init__(self, vector_store):
        self.store = vector_store
        self.original_query = ""

    def _is_skill_query(self, query):
        """Check if query is a short skill-focused search."""
        words = [w for w in query.lower().split() if w not in self.STOP_WORDS]
        # Short query (1-2 meaningful words) or contains known tech skill
        if len(words) <= 2:
            return True
        # Check if any word is a known tech skill
        for word in words:
            if word in self.TECH_SKILLS:
                return True
        return False

    def _expand_with_synonyms(self, keywords):
        """
        Expand keywords with their synonyms for broader matching.
        Returns original keywords plus all their synonyms.
        """
        expanded = set(keywords)
        for word in keywords:
            word_lower = word.lower()
            if word_lower in self.SYNONYMS:
                expanded.update(self.SYNONYMS[word_lower])
        return list(expanded)

    def _get_title_boost(self, query, text):
        """
        Calculate title boost score based on job title matching in query.
        Returns a boost multiplier (1.0 = no boost, up to 1.5 = strong match).
        """
        query_lower = query.lower()
        text_lower = text.lower()

        boost = 1.0

        # Check for job title keywords in query
        title_keywords = ['developer', 'engineer', 'designer', 'manager', 'lead',
                          'senior', 'junior', 'architect', 'analyst', 'scientist']

        for keyword in title_keywords:
            if keyword in query_lower:
                # If the title keyword appears in the document, boost it
                if keyword in text_lower:
                    boost += 0.15

                # Also check title pattern synonyms
                if keyword in self.TITLE_PATTERNS:
                    for synonym in self.TITLE_PATTERNS[keyword]:
                        if synonym in text_lower:
                            boost += 0.1
                            break

        # Check for tech stack in title context
        # e.g., "flutter developer" should boost documents with "flutter" in title context
        query_words = query_lower.split()
        for i, word in enumerate(query_words):
            if word in self.TECH_SKILLS:
                # If next word is a title keyword, this is a "X developer" query
                if i + 1 < len(query_words) and query_words[i + 1] in title_keywords:
                    # Boost if document has this tech skill prominently
                    if word in text_lower[:200]:  # Check in first 200 chars (title/summary area)
                        boost += 0.2

        return min(boost, 1.5)  # Cap at 1.5x boost

    def bm25_score(self, query, documents):
        """
        Improved BM25-like scoring with:
        - Stop word filtering
        - Score normalization to 0-1 range
        - Heavy bonus for exact skill matches
        - Synonym expansion for broader matching
        - Title boosting for job title relevance
        """
        # Extract meaningful keywords (filter stop words, min 2 chars)
        all_words = re.findall(r"\w+", query.lower())
        keywords = [w for w in all_words if w not in self.STOP_WORDS and len(w) >= 2]

        if not keywords:
            keywords = [w for w in all_words if len(w) >= 3]

        # Expand keywords with synonyms for broader matching
        expanded_keywords = self._expand_with_synonyms(keywords)

        scores = {}
        max_score = 0.001  # Avoid division by zero

        for doc_id, text in documents.items():
            text_lower = text.lower()
            score = 0

            # Count keyword matches with bonus for tech skills
            # Use expanded keywords for matching
            for word in expanded_keywords:
                count = text_lower.count(word)
                if count > 0:
                    # Base score with log scale
                    base = 1 + math.log(1 + count)

                    # BIG bonus if it's a tech skill (3x multiplier)
                    if word in self.TECH_SKILLS:
                        base *= 3

                    # Slightly lower weight for synonym matches vs original keywords
                    if word not in keywords:
                        base *= 0.8  # 80% weight for synonym matches

                    score += base

            # Bonus for exact phrase match
            if query.lower() in text_lower:
                score += len(keywords) * 2

            # Apply title boost multiplier
            title_boost = self._get_title_boost(query, text)
            score *= title_boost

            scores[doc_id] = score
            max_score = max(max_score, score)

        # Normalize to 0-1 range
        if max_score > 0:
            scores = {doc_id: s / max_score for doc_id, s in scores.items()}

        return scores

    def search(self, query, filters=None, k=20):
        """
        Hybrid search with dynamic weights based on query type.

        - Skill queries (flutter, react): 80% keyword, 20% semantic
        - Job descriptions: 60% semantic, 40% keyword
        """
        # 1️⃣ Semantic Search (vector similarity)
        vector_results = self.store.search(
            query_embedding=query,
            n_results=k,
            where=filters
        )

        # Handle empty results
        if not vector_results["ids"] or not vector_results["ids"][0]:
            return [], {}

        docs = {}
        vector_scores = {}

        for i, doc_id in enumerate(vector_results["ids"][0]):
            docs[doc_id] = vector_results["documents"][0][i]

            # Convert distance to similarity score (0-1 range)
            distance = vector_results["distances"][0][i]
            vector_scores[doc_id] = 1 / (1 + distance)

        logger.info(f"[HYBRID] ChromaDB returned {len(docs)} chunks")

        # 2️⃣ Keyword Search (BM25-like)
        bm25_scores = self.bm25_score(self.original_query, docs)

        # 3️⃣ Dynamic weights based on query type
        is_skill = self._is_skill_query(self.original_query)

        if is_skill:
            # Short skill query: prioritize keyword matching
            semantic_weight = 0.2
            keyword_weight = 0.8
            logger.info(f"[HYBRID] Query type: SKILL → weights: {keyword_weight*100:.0f}% keyword, {semantic_weight*100:.0f}% semantic")
        else:
            # Job description: balance semantic understanding
            semantic_weight = 0.6
            keyword_weight = 0.4
            logger.info(f"[HYBRID] Query type: JOB_DESC → weights: {semantic_weight*100:.0f}% semantic, {keyword_weight*100:.0f}% keyword")

        # 4️⃣ Merge Scores
        final_scores = defaultdict(float)

        for doc_id in docs:
            semantic = vector_scores.get(doc_id, 0)
            keyword = bm25_scores.get(doc_id, 0)

            # Weighted combination
            final_scores[doc_id] = semantic_weight * semantic + keyword_weight * keyword

        # Sort by score descending
        ranked = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked, docs
