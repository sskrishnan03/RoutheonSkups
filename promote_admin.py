import sqlite3
import os
import sys

db_path = os.path.join('database', 'db.sqlite3')

def promote(email):
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE user SET is_admin = 1 WHERE email = ?", (email,))
        if cursor.rowcount > 0:
            print(f"User {email} promoted to admin successfully.")
        else:
            print(f"User {email} not found.")
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        promote(sys.argv[1])
    else:
        # Default to admin@s76.ai
        promote("admin@s76.ai")
