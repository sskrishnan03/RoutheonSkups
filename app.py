from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from extensions import bcrypt, mail
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

oauth = OAuth()


def _sanitize_proxy_env():
    bad_proxy_markers = ('127.0.0.1:9', 'localhost:9')
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']
    for key in proxy_vars:
        value = (os.environ.get(key) or '').strip().lower()
        if any(marker in value for marker in bad_proxy_markers):
            os.environ.pop(key, None)


def create_app():
    _sanitize_proxy_env()
    application = Flask(__name__)
    application.config.from_object(Config)
    application.wsgi_app = ProxyFix(application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

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

    with application.app_context():
        db.create_all()

    try:
        from scheduler import start_scheduler
        start_scheduler(interval_hours=3)
    except Exception as e:
        logger.exception("Failed to start notification scheduler: %s", e)

    return application


if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
