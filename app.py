from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

logger = logging.getLogger(__name__)

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

oauth = OAuth()
mail = Mail()

def _sanitize_proxy_env():
    bad_proxy_markers = ('127.0.0.1:9', 'localhost:9')
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']
    for key in proxy_vars:
        value = (os.environ.get(key) or '').strip().lower()
        if any(marker in value for marker in bad_proxy_markers):
            os.environ.pop(key, None)


def create_app():
    _sanitize_proxy_env()
    app = Flask(__name__)
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)

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

    from routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    try:
        from scheduler import start_scheduler
        start_scheduler(interval_hours=3)
    except Exception as e:
        logger.exception("Failed to start notification scheduler: %s", e)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
