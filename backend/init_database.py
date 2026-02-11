#!/usr/bin/env python3
"""
Database Initialization Script for TalentGrid
Run this after creating the database in pgAdmin 4
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def init_database(database_url: str):
    """Initialize database with tables"""
    
    print("🔧 Initializing TalentGrid Database...")
    print(f"📍 Connecting to: {database_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"\n✅ Connected to PostgreSQL")
            print(f"   Version: {version}\n")
        
        # Import models (this triggers table creation)
        from app.database import Base
        from app.models import User, Candidate, CVFile
        
        # Create all tables
        print("📋 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Database initialization complete!")
        print("\n📊 Created tables:")
        print("   - users")
        print("   - candidates")
        print("   - cv_files")
        
        print("\n🎯 Next steps:")
        print("   1. Start the FastAPI server: python -m uvicorn app.main:app --reload")
        print("   2. Visit http://localhost:8000/docs for API documentation")
        print("   3. Register a user at /api/auth/register")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check that 'talent_grid' database exists in pgAdmin 4")
        print("   3. Verify DATABASE_URL in .env file")
        print("   4. Check PostgreSQL credentials")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        print("\n💡 Please create .env file from .env.example and set DATABASE_URL")
        sys.exit(1)
    
    success = init_database(database_url)
    sys.exit(0 if success else 1)
