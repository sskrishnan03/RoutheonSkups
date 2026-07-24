from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    preferences = db.Column(db.JSON, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trips = db.relationship('Trip', backref='author', lazy=True)
    saved_destinations = db.relationship('SavedDestination', backref='user', lazy=True)
    favorite_destinations = db.relationship('FavoriteDestination', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    destination_activities = db.relationship('DestinationActivity', backref='user', lazy=True)
    contact_submissions = db.relationship('ContactSubmission', backref='user', lazy=True)
    api_usage_logs = db.relationship('ApiUsageLog', backref='user', lazy=True)
    page_analytics = db.relationship('PageAnalytic', backref='user', lazy=True)
    admin_logs = db.relationship('AdminLog', backref='admin_user', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)


class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.String(50), nullable=True)
    interests = db.Column(db.Text, nullable=True)
    itinerary_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Destination(db.Model):
    __tablename__ = 'destinations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    age_group = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    timings = db.Column(db.String(100), nullable=True)
    best_time = db.Column(db.String(100), nullable=True)
    weather_city = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Itinerary(db.Model):
    __tablename__ = 'itineraries'
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    plan_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedDestination(db.Model):
    __tablename__ = 'saved_destinations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(50), nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FavoriteDestination(db.Model):
    __tablename__ = 'favorite_destinations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(50), nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default='info')
    is_read = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DestinationActivity(db.Model):
    __tablename__ = 'destination_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    destination_name = db.Column(db.String(200), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    extra_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactSubmission(db.Model):
    __tablename__ = 'contact_submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(50), nullable=False)
    trip_reference = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    consent = db.Column(db.Boolean, default=False)
    email_sent_to_admin = db.Column(db.Boolean, default=False)
    email_sent_to_user = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ApiUsageLog(db.Model):
    __tablename__ = 'api_usage_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    service = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)
    latency_ms = db.Column(db.Integer, nullable=True)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PageAnalytic(db.Model):
    __tablename__ = 'page_analytics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    page = db.Column(db.String(200), nullable=False)
    action = db.Column(db.String(50), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WeatherCache(db.Model):
    __tablename__ = 'weather_cache'
    id = db.Column(db.Integer, primary_key=True)
    city_key = db.Column(db.String(200), nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)


class ImageSearchCache(db.Model):
    __tablename__ = 'image_search_cache'
    id = db.Column(db.Integer, primary_key=True)
    query_hash = db.Column(db.String(64), nullable=False, index=True)
    query_text = db.Column(db.String(500), nullable=False)
    images = db.Column(db.JSON, nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)


class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
