from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config import Config
from models import db, User
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

oauth = OAuth()
bcrypt = Bcrypt()
mail = Mail()


def _sanitize_proxy_env():
    bad_proxy_markers = ('127.0.0.1:9', 'localhost:9')
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']
    for key in proxy_vars:
        value = (os.environ.get(key) or '').strip().lower()
        if any(marker in value for marker in bad_proxy_markers):
            os.environ.pop(key, None)


def _migrate_columns(database):
    try:
        from sqlalchemy import text
        uri = database.engine.url.database if hasattr(database.engine.url, 'database') else ''
        if 'sqlite' in str(database.engine.url):
            return
        with database.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='image_url'"
            ))
            row = result.fetchone()
            if row and row[0] != 'text':
                conn.execute(text("ALTER TABLE users ALTER COLUMN image_url TYPE text"))
                conn.commit()
                logger.info("Migrated users.image_url to TEXT.")
    except Exception as e:
        logger.warning("Column migration skipped: %s", e)


def create_app():
    _sanitize_proxy_env()
    application = Flask(__name__)
    application.config.from_object(Config)
    application.wsgi_app = ProxyFix(application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    db_uri = application.config.get('SQLALCHEMY_DATABASE_URI', '')
    logger.info("Database URI starts with: %s...", db_uri[:20] if db_uri else 'EMPTY')

    db.init_app(application)
    bcrypt.init_app(application)
    login_manager.init_app(application)
    oauth.init_app(application)
    mail.init_app(application)

    oauth.register(
        name='google',
        client_id=application.config['GOOGLE_CLIENT_ID'],
        client_secret=application.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes import main_bp
    application.register_blueprint(main_bp)

    try:
        with application.app_context():
            db.create_all()
            _migrate_columns(db)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.exception("Database initialization failed: %s", e)

    try:
        from scheduler import start_scheduler
        start_scheduler(application)
    except Exception as e:
        logger.exception("Failed to start scheduler: %s", e)

    return application


if __name__ == '__main__':
    application = create_app()
    port = int(os.environ.get('PORT', 8000))
    application.run(host='0.0.0.0', port=port, debug=True)
