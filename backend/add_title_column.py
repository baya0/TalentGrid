#!/usr/bin/env python3
"""
Migration script to sync candidates table with SQLAlchemy model.
"""
from app.database import engine
from sqlalchemy import text


def main():
    print("=" * 60)
    print("TalentGrid Database Migration")
    print("=" * 60)

    # ALL columns from the Candidate model
    columns_to_add = [
        # Basic info
        ("name", "VARCHAR(255) NOT NULL DEFAULT 'Unknown'"),
        ("email", "VARCHAR(255)"),
        ("phone", "VARCHAR(50)"),
        ("title", "VARCHAR(255)"),
        ("location", "VARCHAR(255)"),
        ("summary", "TEXT"),
        ("years_experience", "INTEGER DEFAULT 0"),
        # Array column
        ("skills", "VARCHAR[] DEFAULT '{}'"),
        # JSONB columns
        ("languages", "JSONB DEFAULT '[]'::jsonb"),
        ("education", "JSONB DEFAULT '[]'::jsonb"),
        ("experience", "JSONB DEFAULT '[]'::jsonb"),
        ("certifications", "JSONB DEFAULT '[]'::jsonb"),
        ("projects", "JSONB DEFAULT '[]'::jsonb"),
        ("links", "JSONB DEFAULT '{}'::jsonb"),
        ("parsed_data", "JSONB"),
        # AI/RAG fields
        ("quality_score", "NUMERIC(5,2)"),
        ("match_percentage", "INTEGER DEFAULT 0"),
        ("ai_summary", "TEXT"),
        # Metadata
        ("source", "VARCHAR(100)"),
        ("status", "VARCHAR(50) DEFAULT 'new'"),
        ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT NOW()"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE"),
    ]

    with engine.connect() as conn:
        # First, show current state
        result = conn.execute(
            text(
                """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'candidates'
        """
            )
        )
        existing_columns = {row[0] for row in result}
        print(f"\nExisting columns in database: {len(existing_columns)}")

        # Add missing columns
        print("\n" + "-" * 60)
        print("Adding/verifying columns...")
        print("-" * 60)

        added_count = 0
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(
                    text(
                        f"ALTER TABLE candidates ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
                    )
                )
                if col_name not in existing_columns:
                    print(f"✓ ADDED: {col_name}")
                    added_count += 1
                else:
                    print(f"  OK: {col_name}")
            except Exception as e:
                print(f"  Note for {col_name}: {e}")

        conn.commit()
        print(f"\nAdded {added_count} new columns.")

        # Create indexes
        print("\n" + "-" * 60)
        print("Creating indexes...")
        print("-" * 60)
        indexes = [
            ("ix_candidates_name", "name"),
            ("ix_candidates_email", "email"),
            ("ix_candidates_title", "title"),
            ("ix_candidates_status", "status"),
            ("ix_candidates_source", "source"),
        ]

        for idx_name, col_name in indexes:
            try:
                conn.execute(
                    text(
                        f"CREATE INDEX IF NOT EXISTS {idx_name} ON candidates({col_name})"
                    )
                )
                print(f"✓ Index: {idx_name}")
            except Exception as e:
                print(f"  Note for index {idx_name}: {e}")

        conn.commit()

        # Count existing candidates
        result = conn.execute(text("SELECT COUNT(*) FROM candidates"))
        count = result.scalar()
        print(f"\n" + "=" * 60)
        print(f"✅ Current candidates in database: {count}")
        print("=" * 60)

        if count > 0:
            # Show recent candidates
            result = conn.execute(
                text(
                    """
                SELECT id, name, email, created_at
                FROM candidates
                ORDER BY created_at DESC
                LIMIT 5
            """
                )
            )
            print("\nRecent candidates:")
            for row in result:
                print(f"  - ID {row[0]}: {row[1]} ({row[2]})")

    print("\nMigration complete! Restart your backend if needed.")


if __name__ == "__main__":
    main()
