"""
Database migration script for RoutheonSkups (PostgreSQL via Neon).

This replaces the old SQLite migration script.
Run this after updating models.py to apply schema changes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from models import db


def migrate():
    app = create_app()
    with app.app_context():
        print("Connecting to Neon PostgreSQL...")
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        masked = db_uri[:35] + '...' if len(db_uri) > 40 else db_uri
        print(f"Database: {masked}")

        print("\nApplying schema (db.create_all)...")
        db.create_all()

        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = sorted(inspector.get_table_names())
        print(f"\nAll {len(tables)} tables verified on Neon PostgreSQL.")
        for t in tables:
            cols = [c['name'] for c in inspector.get_columns(t)]
            print(f"  {t} ({len(cols)} columns)")


if __name__ == "__main__":
    migrate()
