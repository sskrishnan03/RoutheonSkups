import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from models import db


def init_neon_database():
    app = create_app()
    with app.app_context():
        print("Connecting to Neon PostgreSQL...")
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print(f"Database URI: {db_uri[:30]}...{db_uri[-20:]}" if len(db_uri) > 50 else f"Database URI: {db_uri}")

        print("\nCreating all 16 tables...")
        db.create_all()

        print("\nVerifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        tables.sort()

        expected_tables = [
            'admin_logs',
            'api_usage_log',
            'chat_messages',
            'chat_sessions',
            'contact_submissions',
            'destination_activities',
            'destinations',
            'favorite_destinations',
            'image_search_cache',
            'itineraries',
            'notifications',
            'page_analytics',
            'saved_destinations',
            'trips',
            'users',
            'weather_cache',
        ]

        print(f"\n{'='*50}")
        print(f"{'TABLE':<35} {'STATUS':<15}")
        print(f"{'='*50}")

        all_ok = True
        for table in expected_tables:
            if table in tables:
                cols = [col['name'] for col in inspector.get_columns(table)]
                print(f"  {table:<33} CREATED ({len(cols)} cols)")
            else:
                print(f"  {table:<33} MISSING!")
                all_ok = False

        for table in tables:
            if table not in expected_tables:
                print(f"  {table:<33} EXTRA (not expected)")

        print(f"\n{'='*50}")
        if all_ok:
            print("ALL 16 TABLES CREATED SUCCESSFULLY ON NEON!")
        else:
            print("WARNING: Some tables are missing. Check errors above.")
        print(f"Total tables found: {len(tables)}")
        print(f"{'='*50}")


if __name__ == '__main__':
    init_neon_database()
