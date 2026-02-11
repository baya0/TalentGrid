#!/usr/bin/env python3
"""
Re-index all existing candidates from the database into ChromaDB.
This allows the AI search to find candidates that were imported before
sentence-transformers was installed.
"""
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Set defaults if environment variables are missing
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/talent_grid"
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-secret-key-for-reindex-script"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.candidate import Candidate
from app.config import settings
from app.ai.service import AIService

def main():
    print("=" * 60)
    print("Re-indexing Candidates into ChromaDB Vector Store")
    print("=" * 60)
    print("Using embedding model: all-mpnet-base-v2 (768 dimensions)")

    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Get all candidates
    candidates = session.query(Candidate).all()
    total = len(candidates)

    print(f"\nFound {total} candidates in database")

    if total == 0:
        print("No candidates to index. Import some CVs first!")
        return

    # Initialize AI service
    print("\nInitializing AI service (loading embedding model)...")
    ai_service = AIService()

    # Clear existing vector store (required when changing embedding models)
    print("Clearing existing vector store for fresh re-index...")
    ai_service.clear_vector_store()

    success_count = 0
    error_count = 0

    print("\nIndexing candidates:\n")

    for i, candidate in enumerate(candidates, 1):
        # Build CV data structure from candidate record
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
                success_count += 1
                print(f"  [{i}/{total}] ✓ {candidate.name}")
            else:
                error_count += 1
                print(f"  [{i}/{total}] ✗ {candidate.name} (failed)")
        except Exception as e:
            error_count += 1
            print(f"  [{i}/{total}] ✗ {candidate.name} - Error: {e}")

    print("\n" + "=" * 60)
    print(f"Indexing complete!")
    print(f"  ✓ Success: {success_count}")
    print(f"  ✗ Failed:  {error_count}")
    print("=" * 60)

    # Verify ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = client.list_collections()
        for coll in collections:
            count = coll.count()
            print(f"\nChromaDB collection '{coll.name}': {count} documents")
    except Exception as e:
        print(f"\nWarning: Could not verify ChromaDB: {e}")

    session.close()

if __name__ == "__main__":
    main()
