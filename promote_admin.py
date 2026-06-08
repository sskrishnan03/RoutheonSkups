import sqlite3
import os
import sys

db_path = os.path.join('database', 'db.sqlite3')

def set_admin(email, is_admin):
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE user SET is_admin = ? WHERE email = ?", (is_admin, email))
        if cursor.rowcount > 0:
            if is_admin:
                print(f"User {email} promoted to admin successfully.")
            else:
                print(f"User {email} removed from admin successfully.")
        else:
            print(f"User {email} not found.")
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def promote(email):
    set_admin(email, 1)


def remove_admin(email):
    set_admin(email, 0)

if __name__ == "__main__":
    # Usage:
    #   python promote_admin.py <email>
    #   python promote_admin.py remove <email>
    if len(sys.argv) == 2:
        promote(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[1].lower() == "remove":
        remove_admin(sys.argv[2])
    else:
        print("Usage:")
        print("  python promote_admin.py <email>")
        print("  python promote_admin.py remove <email>")
