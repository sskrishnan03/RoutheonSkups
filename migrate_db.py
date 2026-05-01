import sqlite3
import os

def migrate():
    db_path = 'database/db.sqlite3'
    if not os.path.exists(db_path):
        # Create directory if missing
        os.makedirs('database', exist_ok=True)
        print(f"Database not found at {db_path}, it will be created on first run.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if phone column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'phone' not in columns:
            print("Adding 'phone' column to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN phone VARCHAR(20)")
        
        if 'city' not in columns:
            print("Adding 'city' column to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN city VARCHAR(100)")
            
        conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
