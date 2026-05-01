from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
import os
import sqlite3

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

oauth = OAuth()
mail = Mail()


def _apply_sqlite_schema_updates(app):
    database_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not database_uri.startswith('sqlite:///'):
        return

    db_path = database_uri.replace('sqlite:///', '', 1)
    if not os.path.isabs(db_path):
        db_path = os.path.join(app.root_path, db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    expected_columns = {
        'user': ['created_at', 'updated_at'],
        'trip': ['created_at', 'updated_at'],
        'destination': ['created_at', 'updated_at'],
        'itinerary': ['created_at', 'updated_at'],
        'saved_destination': ['created_at', 'updated_at'],
        'notification': ['created_at', 'updated_at'],
        'chat_session': ['created_at', 'updated_at'],
        'chat_message': ['created_at', 'updated_at'],
    }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        for table_name, columns in expected_columns.items():
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                continue

            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = {row[1] for row in cursor.fetchall()}

            for column in columns:
                if column in existing_columns:
                    continue
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} DATETIME")
                cursor.execute(f"UPDATE {table_name} SET {column}=CURRENT_TIMESTAMP WHERE {column} IS NULL")

        conn.commit()
    finally:
        conn.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)

    # Register Google OAuth provider
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        _apply_sqlite_schema_updates(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
