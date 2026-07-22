from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, Response, session
from models import db, User, Trip, Destination, Itinerary, SavedDestination, FavoriteDestination, Notification, ChatSession, ChatMessage, DestinationActivity
from services import AIService, WeatherService
# from graph_service import graph_service
import json
from datetime import datetime, timedelta, timezone, date
import random
from flask_login import login_user, current_user, logout_user, login_required
from app import bcrypt, mail
from flask_mail import Message
import os
import mimetypes
import html
import base64
import csv
from io import StringIO
from uuid import uuid4
from werkzeug.utils import secure_filename
from sqlalchemy import func
from authlib.integrations.base_client.errors import MismatchingStateError
from global_countries import (
    get_all_destination_names, get_daily_destinations, get_country_info,
    get_tts_voice, get_tts_fallback_lang, search_destinations,
    get_country_center_coords, ALL_COUNTRY_NAMES, ALL_COUNTRIES_BY_CODE
)

main_bp = Blueprint('main', __name__)

DEFAULT_NOTIFICATION_SETTINGS = {
    'notifications_enabled': True,
    'trip_alerts': True,
    'ai_suggestions': True,
    'system_notifications': True,
    'seasonal_recommendations': True,
    'email_notifications': True
}

DEFAULT_AI_ASSISTANT_SETTINGS = {
    'proactive_tips': True,
    'chat_history': True
}

PROFILE_UPLOAD_DIR = os.path.join('uploads', 'profile_images')
ALLOWED_PROFILE_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}


def _fallback_response(payload, fallback_message):
    result = payload if isinstance(payload, dict) else {"data": payload}
    has_error = bool(result.get("error"))
    result["fallback"] = has_error
    result["fallback_message"] = fallback_message if has_error else ""
    return result


def _mark_fallback(result, fallback_message, is_fallback):
    result["fallback"] = bool(is_fallback)
    result["fallback_message"] = fallback_message if is_fallback else ""
    return result


def _sanitize_icon_name(raw_icon):
    text = str(raw_icon or '').strip().lower()
    text = ''.join(ch for ch in text if ch.isalnum() or ch in {'_', ' '}).replace(' ', '_')
    if not text:
        return 'place'
    alias = {
        'place_of_worship': 'temple_hindu',
        'monument': 'account_balance',
        'heritage': 'castle',
        'history': 'history_edu',
        'spiritual': 'temple_hindu',
        'beach': 'beach_access',
        'hill_station': 'terrain',
        'hills': 'terrain',
        'nature': 'landscape',
        'wildlife': 'pets',
        'food': 'restaurant',
        'temple': 'temple_hindu'
    }
    if text in alias:
        return alias[text]
    if text.startswith(('fa_', 'fas_', 'far_', 'fab_', 'mdi_', 'icon_')):
        return 'place'
    if 2 <= len(text) <= 32:
        return text
    return 'place'


def _sanitize_tag_text(raw_tag):
    text = str(raw_tag or 'Destination').replace('_', ' ').replace('-', ' ')
    text = ' '.join(text.split()).strip()
    if not text:
        return 'Destination'
    return text[:24]


def _sanitize_destination_payload_icons(data):
    if not isinstance(data, dict):
        return data
    if isinstance(data.get('destinations'), list):
        for item in data['destinations']:
            if isinstance(item, dict):
                item['icon'] = _sanitize_icon_name(item.get('icon'))
                item['tag'] = _sanitize_tag_text(item.get('tag'))
    if isinstance(data.get('attractions'), list):
        for item in data['attractions']:
            if isinstance(item, dict):
                item['icon'] = _sanitize_icon_name(item.get('icon'))
                item['tag'] = _sanitize_tag_text(item.get('tag'))
    if isinstance(data.get('days'), list):
        for day in data['days']:
            if not isinstance(day, dict):
                continue
            for act in (day.get('activities') or []):
                if isinstance(act, dict):
                    act['icon'] = _sanitize_icon_name(act.get('icon'))
    if isinstance(data.get('itinerary'), list):
        for day in data['itinerary']:
            if not isinstance(day, dict):
                continue
            for act in (day.get('activities') or []):
                if isinstance(act, dict):
                    act['icon'] = _sanitize_icon_name(act.get('icon'))
    return data


def _track_activity(user, destination_name, action_type, extra_data=None):
    try:
        activity = DestinationActivity(
            user_id=user.id if user else None,
            destination_name=destination_name[:200],
            action_type=action_type,
            extra_data=extra_data or {}
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Track activity error: {e}")


def _is_local_profile_image(image_url):
    if not image_url:
        return False
    normalized = str(image_url).replace('\\', '/')
    return normalized.startswith('/static/uploads/profile_images/')


def _delete_local_profile_image(image_url):
    if not _is_local_profile_image(image_url):
        return
    relative_path = str(image_url).replace('/static/', '', 1).replace('/', os.sep)
    absolute_path = os.path.join(current_app.root_path, 'static', relative_path)
    if os.path.isfile(absolute_path):
        os.remove(absolute_path)

GLOBAL_PROMPT_DESTINATIONS = [
    "Goa", "Jaipur", "Udaipur", "Jaisalmer", "Rishikesh", "Manali", "Shimla", "Dharamshala",
    "Leh", "Srinagar", "Amritsar", "Varanasi", "Agra", "Delhi", "Mumbai", "Pune", "Bengaluru",
    "Mysuru", "Coorg", "Ooty", "Kodaikanal", "Chennai", "Pondicherry", "Hyderabad", "Hampi",
    "Kochi", "Munnar", "Alleppey", "Thekkady", "Madurai", "Kolkata", "Darjeeling", "Gangtok",
    "Kyoto", "Tokyo", "Osaka", "Hiroshima", "Nara", "Hakone",
    "Paris", "Nice", "Lyon", "Marseille", "Bordeaux", "Strasbourg",
    "Rome", "Florence", "Venice", "Amalfi", "Cinque Terre", "Milan",
    "Barcelona", "Madrid", "Seville", "Granada", "Ibiza", "Valencia",
    "New York", "Los Angeles", "San Francisco", "Las Vegas", "Miami", "Chicago",
    "Queenstown", "Auckland", "Rotorua", "Wellington",
    "Santorini", "Athens", "Mykonos", "Crete",
    "Zurich", "Interlaken", "Lucerne", "Geneva",
    "Sydney", "Melbourne", "Brisbane", "Perth",
    "Bangkok", "Chiang Mai", "Phuket", "Krabi",
    "London", "Edinburgh", "Bath", "Oxford",
    "Toronto", "Vancouver", "Montreal",
    "Istanbul", "Cappadocia", "Antalya",
    "Cairo", "Luxor", "Alexandria",
    "Cape Town", "Johannesburg", "Durban",
    "Reykjavik", "Bali", "Hanoi", "Ha Long Bay",
    "Berlin", "Munich", "Hamburg", "Frankfurt",
    "Seoul", "Busan", "Jeju",
    "Dubai", "Abu Dhabi", "Amsterdam", "Rotterdam",
    "Dubrovnik", "Split", "Plitvice Lakes", "Hvar",
    "Dublin", "Galway", "Cork", "Killarney",
    "Marina Bay", "Sentosa", "Gardens by the Bay",
    "Prague", "Cesky Krumlov", "Karlovy Vary", "Brno",
    "Sigiriya", "Kandy", "Galle", "Ella",
    "Marrakech", "Fez", "Chefchaouen", "Essaouira",
    "Buenos Aires", "Bariloche", "El Calafate", "Ushuaia",
    "Helsinki", "Rovaniemi", "Levi", "Lapland",
    "Beijing", "Shanghai", "Xi'an", "Guilin", "Chengdu"
]


def _get_daily_ai_inspiration_prompts():
    """Return 15 global trip prompt inspirations that rotate daily (UTC)."""
    today = datetime.utcnow().date()
    rng = random.Random(f"daily-ai-prompts-{today.isoformat()}")

    durations = [3, 4, 5, 6, 7, 8, 9, 10]
    groups = [
        "solo traveler", "couple", "friends", "family with kids", "parents",
        "group of 4", "group of 6", "newly married couple"
    ]
    focus_areas = [
        "local food trails and cultural walks",
        "nature viewpoints and photography spots",
        "adventure activities with moderate budget",
        "spiritual places and peaceful stays",
        "heritage sites and guided city tours",
        "offbeat cafes and local markets",
        "sunrise and sunset points",
        "waterfalls, forests and short hikes",
        "shopping streets and evening experiences",
        "relaxed itinerary with less travel time"
    ]

    destinations = GLOBAL_PROMPT_DESTINATIONS[:]
    rng.shuffle(destinations)

    prompts = []
    for i in range(15):
        destination = destinations[i % len(destinations)]
        duration = rng.choice(durations)
        group = rng.choice(groups)
        focus = rng.choice(focus_areas)
        prompts.append(
            f"Plan a {duration}-day trip to {destination} for a {group}, focusing on {focus}."
        )

    # Keep order changing per day while stable for that day.
    rng.shuffle(prompts)
    return prompts


def _get_user_preferences(user):
    raw = user.preferences if isinstance(user.preferences, dict) else {}
    prefs = dict(raw)
    categories = prefs.get('categories', [])
    if isinstance(categories, str):
        categories = [c.strip() for c in categories.split(',') if c.strip()]
    elif not isinstance(categories, list):
        categories = []
    # Normalize to a unique ordered list of non-empty strings.
    cleaned = []
    seen = set()
    for cat in categories:
        text = str(cat).strip()
        if text and text not in seen:
            seen.add(text)
            cleaned.append(text)
    prefs['categories'] = cleaned
    return prefs


def _get_notification_settings(user):
    prefs = _get_user_preferences(user)
    current = prefs.get('notification_settings', {}) if isinstance(prefs.get('notification_settings', {}), dict) else {}
    merged = DEFAULT_NOTIFICATION_SETTINGS.copy()
    merged.update(current)
    return merged


def _set_user_notification_settings(user, new_settings):
    prefs = _get_user_preferences(user)
    prefs['notification_settings'] = new_settings
    user.preferences = prefs


def _set_notification_meta(user, meta):
    prefs = _get_user_preferences(user)
    prefs['notification_meta'] = meta
    user.preferences = prefs


def _get_ai_assistant_settings(user):
    prefs = _get_user_preferences(user)
    current = prefs.get('ai_assistant_settings', {}) if isinstance(prefs.get('ai_assistant_settings', {}), dict) else {}
    merged = DEFAULT_AI_ASSISTANT_SETTINGS.copy()
    merged.update(current)
    return merged


def _set_ai_assistant_settings(user, new_settings):
    prefs = _get_user_preferences(user)
    prefs['ai_assistant_settings'] = new_settings
    user.preferences = prefs


def _get_pinned_chat_session_ids(user):
    prefs = _get_user_preferences(user)
    pinned = prefs.get('pinned_chat_sessions', [])
    if not isinstance(pinned, list):
        return []
    return [int(x) for x in pinned if str(x).isdigit()]


def _set_pinned_chat_session_ids(user, pinned_ids):
    prefs = _get_user_preferences(user)
    prefs['pinned_chat_sessions'] = sorted(list({int(x) for x in pinned_ids}))
    user.preferences = prefs


def _notification_display_name(user):
    full_name = (getattr(user, 'name', '') or '').strip()
    return full_name if full_name else "Traveler"


def _get_mail_sender(purpose):
    sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
    required_config = {
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': current_app.config.get('MAIL_PASSWORD'),
    }
    missing = [key for key, value in required_config.items() if not value]
    if not sender:
        missing.append('MAIL_DEFAULT_SENDER')
    if missing:
        current_app.logger.warning("%s email skipped: missing mail config %s.", purpose, ", ".join(missing))
        return None
    return sender


def _send_mail_message(msg, purpose, user_id=None):
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.exception("%s email send error for user_id=%s: %s", purpose, user_id, e)
        return False


def _create_notification(user, message, notif_type='info', email_subject=None):
    notif = Notification(user_id=user.id, message=message, type=notif_type)
    db.session.add(notif)
    return notif, email_subject or "RoutheonSkups Notification"


def _send_notification_email(user, subject, message, created_at=None):
    if not user.email:
        current_app.logger.warning("Notification email skipped: user has no email address.")
        return False
    sender = _get_mail_sender("Notification")
    if not sender:
        return False
    display_name = _notification_display_name(user)
    sent_at = created_at.strftime('%d %b %Y, %I:%M %p UTC') if created_at else datetime.now(timezone.utc).strftime('%d %b %Y, %I:%M %p UTC')
    msg = Message(subject=subject, recipients=[user.email], sender=sender)
    msg.body = (
        f"Hi {display_name},\n\n"
        "Here is a quick update from RoutheonSkups.\n\n"
        f"Time: {sent_at}\n"
        f"Message: {message}\n\n"
        "Open RoutheonSkups to see the full details.\n\n"
        "RoutheonSkups Team"
    )
    return _send_mail_message(msg, "Notification", getattr(user, 'id', None))


def _send_password_reset_email(user):
    if not user.email:
        current_app.logger.warning("Password reset email skipped: user has no email address.")
        return False
    sender = _get_mail_sender("Password reset")
    if not sender:
        return False
    token = user.get_reset_token()
    reset_url = url_for('main.reset_token', token=token, _external=True)
    msg = Message(
        subject='Reset Your Password — RoutheonSkups',
        recipients=[user.email],
        sender=sender
    )
    msg.body = f'''RoutheonSkups

Your gateway to smarter travel planning. Plan trips, explore destinations, and discover the world like never before.

Reset your password here:
{reset_url}

If you didn't request this, you can safely ignore this email.'''
    msg.html = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#000000;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#000000;padding:40px 20px;">
<tr><td align="center">
  <h1 style="margin:0 0 8px;font-size:22px;font-weight:800;color:#FFFFFF;letter-spacing:-0.02em;">RoutheonSkups</h1>
  <p style="margin:0 0 24px;font-size:13px;color:rgba(255,255,255,0.4);font-style:italic;">Your gateway to smarter travel planning. Plan trips, explore destinations, and discover the world like never before.</p>
  <a href="{reset_url}" style="display:inline-block;padding:12px 32px;background:#FFFFFF;color:#000000;font-size:14px;font-weight:700;text-decoration:none;border-radius:8px;">Reset Password</a>
  <p style="margin:24px 0 0;font-size:12px;color:rgba(255,255,255,0.35);">If you didn't request this, you can safely ignore this email.</p>
</td></tr>
</table>
</body>
</html>'''
    return _send_mail_message(msg, "Password reset", getattr(user, 'id', None))


def _notification_email_subject(notif):
    subject_by_type = {
        'trip': 'Trip Alert from RoutheonSkups',
        'success': 'RoutheonSkups Update',
        'warning': 'System Notification',
        'info': 'RoutheonSkups Notification'
    }
    return subject_by_type.get((getattr(notif, 'type', '') or '').lower(), 'RoutheonSkups Notification')


def _send_notification_record_email(user, notif, subject=None):
    if getattr(notif, 'email_sent_at', None):
        return False
    if _send_notification_email(user, subject or _notification_email_subject(notif), notif.message, notif.created_at):
        notif.email_sent_at = datetime.utcnow()
        return True
    return False


def _send_created_notification_emails(user, created_notifications):
    if not created_notifications:
        return 0
    settings = _get_notification_settings(user)
    if not settings.get('email_notifications', True):
        current_app.logger.info("Notification emails disabled for user_id=%s.", getattr(user, 'id', None))
        return 0

    sent_count = 0
    for notif, subject in created_notifications:
        if _send_notification_record_email(user, notif, subject):
            sent_count += 1
    if sent_count:
        db.session.commit()
    return sent_count


def _send_pending_notification_emails(user, limit=50):
    settings = _get_notification_settings(user)
    if not settings.get('email_notifications', True):
        current_app.logger.info("Notification emails disabled for user_id=%s.", getattr(user, 'id', None))
        return 0

    pending = (
        Notification.query
        .filter(Notification.user_id == user.id, Notification.email_sent_at.is_(None))
        .order_by(Notification.created_at.asc())
        .limit(limit)
        .all()
    )
    sent_count = 0
    for notif in pending:
        if _send_notification_record_email(user, notif):
            sent_count += 1
    if sent_count:
        db.session.commit()
    return sent_count


def _generate_smart_notifications(user, force=False):
    settings = _get_notification_settings(user)
    if not settings.get('notifications_enabled', True):
        return 0
    ai_settings = _get_ai_assistant_settings(user)
    now = datetime.utcnow()
    today = now.date()
    prefs = _get_user_preferences(user)
    meta = dict(prefs.get('notification_meta', {}) if isinstance(prefs.get('notification_meta', {}), dict) else {})
    display_name = _notification_display_name(user)
    created = []
    meta_changed = False
    global_cooldown_hours = 24

    if not force:
        last_any_iso = meta.get('last_notification_sent_at')
        if last_any_iso:
            try:
                last_any_dt = datetime.fromisoformat(last_any_iso)
                if now - last_any_dt < timedelta(hours=global_cooldown_hours):
                    return 0
            except Exception:
                pass

    def maybe_add(setting_key, meta_key, cooldown_hours, message, notif_type='info', email_subject=None):
        nonlocal meta_changed
        if not settings.get(setting_key, True):
            return
        last_iso = meta.get(meta_key)
        if not force and last_iso:
            try:
                last_dt = datetime.fromisoformat(last_iso)
                if now - last_dt < timedelta(hours=cooldown_hours):
                    return
            except Exception:
                pass
        created.append(_create_notification(user, message, notif_type, email_subject))
        meta[meta_key] = now.isoformat()
        meta_changed = True

    upcoming_trips = Trip.query.filter(
        Trip.user_id == user.id,
        Trip.start_date >= today
    ).order_by(Trip.start_date.asc()).limit(20).all()

    for trip in upcoming_trips:
        days_left = (trip.start_date - today).days
        if days_left in (0, 1, 3, 7):
            if days_left == 0:
                msg = f"{display_name}, your {trip.destination} trip starts today. Safe travels and enjoy every moment!"
            elif days_left == 1:
                msg = f"{display_name}, your {trip.destination} trip starts tomorrow. A quick pack check now can make tomorrow smoother."
            else:
                msg = f"{display_name}, {trip.destination} starts in {days_left} days. This is a great time to lock your final plan."
            maybe_add('trip_alerts', f"trip_alert:{trip.id}:{days_left}", 24, msg, notif_type='trip', email_subject=f"Trip Alert: {trip.destination}")

    month = now.month
    season_map = {1: "Winter", 2: "Winter", 3: "Summer", 4: "Summer", 5: "Summer", 6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon", 10: "Post-Monsoon", 11: "Winter", 12: "Winter"}
    season = season_map.get(month, "Season")

    saved_names = [s.name for s in SavedDestination.query.filter_by(user_id=user.id).order_by(SavedDestination.created_at.desc()).limit(8).all() if s.name]
    trip_names = [t.destination for t in Trip.query.filter_by(user_id=user.id).order_by(Trip.created_at.desc()).limit(6).all() if t.destination]
    combined_names = []
    for name in saved_names + trip_names:
        if name and name not in combined_names:
            combined_names.append(name)

    if combined_names:
        focus = combined_names[0]
        top_three = ", ".join(combined_names[:3])
        if ai_settings.get('proactive_tips', True):
            maybe_add('ai_suggestions', f"ai_suggestion:{month}:{focus}", 168, f"{display_name}, based on your interest in {focus}, {season} is a great time to explore {top_three}.", notif_type='info', email_subject="AI Suggestion for Your Next Trip")
        maybe_add('seasonal_recommendations', f"seasonal:{month}", 168, f"{display_name}, your {season} picks are ready: {top_three}. Want to start with {focus}?", notif_type='info', email_subject=f"{season} Travel Recommendation")

    month_key = now.strftime('%Y-%m')
    maybe_add('system_notifications', f"system:{month_key}", 720, f"{display_name}, quick system update: reliability checks are complete and your account data looks healthy.", notif_type='warning', email_subject="System Notification")

    if created or meta_changed:
        _set_notification_meta(user, meta)
        meta['last_notification_sent_at'] = now.isoformat()
        _set_notification_meta(user, meta)
        db.session.commit()
        _send_created_notification_emails(user, created)

    return len(created)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    return render_template('firstpage.html')

@main_bp.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    return redirect(url_for('main.landing'))

@main_bp.route('/landing')
@login_required
def landing():
    return render_template('landing_page.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not name or not email or not password:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('main.register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_exists = User.query.filter(db.func.lower(User.email) == email).first()
        if user_exists:
            # Existing Google-only account: allow setting an email password.
            if not user_exists.password:
                user_exists.name = name or user_exists.name
                user_exists.password = hashed_password
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('main.login', mode='email'))
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))

        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login', mode='email'))
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return redirect(url_for('main.login', mode='email'))
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user and user.password and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.landing'))
        else:
            if user and not user.password:
                flash('This account was created with Google. Use Google Sign-In or set a password via Register.', 'danger')
                return redirect(url_for('main.login', mode='email'))
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return redirect(url_for('main.login', mode='email'))
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        user = User.query.filter(db.func.lower(User.email) == email).first()
        
        if user:
            if _send_password_reset_email(user):
                flash('An email has been sent with instructions to reset your password.', 'success')
            else:
                flash('There was an error sending the reset email. Please try again later.', 'danger')
        else:
            # For security reasons, we still show the success message even if the user doesn't exist
            flash('If an account exists with that email, a password reset link has been sent.', 'success')
            
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html')

@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_token.html', token=token)
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('reset_token.html', token=token)

@main_bp.route('/auth/google')
def google_login():
    oauth = current_app.extensions['authlib.integrations.flask_client']
    # Prevent stale state values from earlier aborted OAuth attempts.
    for key in list(session.keys()):
        if str(key).startswith('_state_google_'):
            session.pop(key, None)
    redirect_uri = url_for('main.google_callback', _external=True)
    try:
        return oauth.google.authorize_redirect(redirect_uri, prompt='select_account')
    except Exception:
        flash('Google sign-in is temporarily unavailable. Please try email sign-in.', 'warning')
        return redirect(url_for('main.login', mode='email'))

@main_bp.route('/auth/google/callback')
def google_callback():
    oauth = current_app.extensions['authlib.integrations.flask_client']
    try:
        token = oauth.google.authorize_access_token()
    except MismatchingStateError:
        flash('Google sign-in expired or was interrupted. Please try again.', 'warning')
        return redirect(url_for('main.login', mode='email'))
    except Exception:
        flash('Google sign-in failed due to a network issue. Please try again.', 'danger')
        return redirect(url_for('main.login', mode='email'))
    user_info = token.get('userinfo')
    if not user_info:
        flash('Google authentication failed.', 'danger')
        return redirect(url_for('main.login'))

    google_id = user_info['sub']
    email = user_info['email'].strip().lower()
    name = user_info.get('name', email.split('@')[0])
    picture = user_info.get('picture')
    # Check if user exists by google_id or email
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            # Link existing email user to their Google account
            user.google_id = google_id
            if not user.image_url and picture:
                user.image_url = picture
            db.session.commit()
        else:
            # Create new user
            user = User(name=name, email=email, google_id=google_id, image_url=picture)
            db.session.add(user)
            db.session.commit()
    else:
        db.session.commit()

    login_user(user)
    return redirect(url_for('main.landing'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('main.plan_trip'))

@main_bp.route('/plan-trip')
@login_required
def plan_trip():
    return render_template('plan_a_trip.html')

@main_bp.route('/ai-prompt')
@login_required
def ai_prompt():
    inspiration_prompts = _get_daily_ai_inspiration_prompts()
    return render_template('aipromptplanatrip.html', inspiration_prompts=inspiration_prompts)

@main_bp.route('/api/ai-plan', methods=['POST'])
@login_required
def api_ai_plan():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    plan = AIService.generate_plan_from_prompt(prompt)
    plan = _sanitize_destination_payload_icons(plan)
    return jsonify(_fallback_response(plan, "AI planner is temporarily unavailable. Please retry in a few moments."))

@main_bp.route('/explore')
@login_required
def explore():
    return render_template('explore.html')

@main_bp.route('/my-trips')
@login_required
def my_trips():
    return redirect(url_for('main.profile') + '#trips')

@main_bp.route('/api/trip-cost-estimate', methods=['POST'])
@login_required
def api_trip_cost_estimate():
    data = request.get_json(silent=True) or {}

    def as_non_negative_number(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if number < 0:
            return None
        return number

    travelers = as_non_negative_number(data.get('travelers', 1))
    days = as_non_negative_number(data.get('days', 1))
    stay_per_night = as_non_negative_number(data.get('stay_per_night', 0))
    local_transport_per_day = as_non_negative_number(data.get('local_transport_per_day', 0))
    food_per_day_per_person = as_non_negative_number(data.get('food_per_day_per_person', 0))
    activity_per_person = as_non_negative_number(data.get('activity_per_person', 0))
    misc_cost = as_non_negative_number(data.get('misc_cost', 0))
    round_trip_travel_total = as_non_negative_number(data.get('round_trip_travel_total', 0))

    if None in [travelers, days, stay_per_night, local_transport_per_day, food_per_day_per_person, activity_per_person, misc_cost, round_trip_travel_total]:
        return jsonify({"success": False, "error": "Please enter valid non-negative numbers for all fields."}), 400

    travelers = max(1, int(round(travelers)))
    days = max(1, int(round(days)))
    nights = max(0, days - 1)

    stay_total = stay_per_night * nights
    local_transport_total = local_transport_per_day * days
    food_total = food_per_day_per_person * travelers * days
    activity_total = activity_per_person * travelers
    total = round_trip_travel_total + stay_total + local_transport_total + food_total + activity_total + misc_cost
    per_person = total / travelers if travelers else total
    per_day = total / days if days else total

    return jsonify({
        "success": True,
        "breakdown": {
            "travelers": travelers,
            "days": days,
            "nights": nights,
            "round_trip_travel_total": round(round_trip_travel_total, 2),
            "stay_total": round(stay_total, 2),
            "local_transport_total": round(local_transport_total, 2),
            "food_total": round(food_total, 2),
            "activity_total": round(activity_total, 2),
            "misc_cost": round(misc_cost, 2),
            "total_budget": round(total, 2),
            "per_person_budget": round(per_person, 2),
            "per_day_budget": round(per_day, 2)
        }
    })

@main_bp.route('/favorites')
@login_required
def favorites():
    favorite_destinations = FavoriteDestination.query.filter_by(user_id=current_user.id).order_by(FavoriteDestination.created_at.desc()).all()
    return render_template('favorites.html', favorite_destinations=favorite_destinations)

@main_bp.route('/skupheon')
@login_required
def skupheon():
    return render_template('skupheon.html')

@main_bp.route('/destination/<name>')
@login_required
def destination_info(name):
    data = AIService.get_destination_detail(name)
    lat = data.get('center_coords', {}).get('lat')
    lon = data.get('center_coords', {}).get('lng')
    weather = WeatherService.get_forecast(name, lat=lat, lon=lon)
    _track_activity(current_user, name, 'view')
    return render_template('destination.html', name=name, data=data, weather=weather)

@main_bp.route('/destination/<name>/chatbot')
@login_required
def destination_chatbot(name):
    data = AIService.get_destination_detail(name)
    lat = data.get('center_coords', {}).get('lat')
    lon = data.get('center_coords', {}).get('lng')
    weather = WeatherService.get_forecast(name, lat=lat, lon=lon)
    return render_template('aichatbot.html', name=name, data=data, weather=weather)

@main_bp.route('/create-trip')
@login_required
def create_trip():
    daily_destinations = get_daily_destinations(count=20)

    return render_template('plan_trip_step1.html', popular_destinations=daily_destinations)

@main_bp.route('/plan-trip-step2')
@login_required
def plan_trip_step2():
    destination = request.args.get('destination', '')
    return render_template('plan_trip_step2.html', destination=destination)

@main_bp.route('/plan-trip-step2.0')
@login_required
def plan_trip_step2_0():
    destination = request.args.get('destination', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    flexible = request.args.get('flexible', 'false')
    return render_template('plan_trip_step2.0.html', 
                          destination=destination, 
                          start_date=start_date, 
                          end_date=end_date, 
                          flexible=flexible)

@main_bp.route('/plan-trip-step3')
@login_required
def plan_trip_step3():
    destination = request.args.get('destination', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    flexible = request.args.get('flexible', 'false')
    styles = request.args.get('styles', '')
    return render_template('plan_trip_step3.html', 
                          destination=destination, 
                          start_date=start_date, 
                          end_date=end_date, 
                          flexible=flexible,
                          styles=styles)

@main_bp.route('/plan-trip-step4')
@login_required
def plan_trip_step4():
    return render_template('plan_trip_step4.html')

@main_bp.route('/view-trip/<int:trip_id>')
@login_required
def view_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return "Unauthorized", 403
    
    # Parse saved payload (supports old list-only format and new rich format)
    itinerary = []
    weather = {}
    chat = []
    trip_meta = {}
    try:
        parsed = json.loads(trip.itinerary_text) if trip.itinerary_text else []
        if isinstance(parsed, dict):
            itinerary = parsed.get('itinerary', []) or []
            weather = parsed.get('weather', {}) or {}
            chat = parsed.get('chat', []) or []
            trip_meta = {
                "adults": parsed.get('adults', 2),
                "children": parsed.get('children', 0),
                "budget": parsed.get('budget', trip.budget or 'Comfort')
            }
        elif isinstance(parsed, list):
            itinerary = parsed
    except Exception:
        itinerary = []
    
    live_weather = WeatherService.get_forecast(trip.destination)

    # We can pass this to a dedicated view template or reuse step4 if we adapt it
    return render_template(
        'view_trip.html',
        trip=trip,
        itinerary=itinerary,
        weather=weather,
        live_weather=live_weather,
        chat=chat,
        trip_meta=trip_meta
    )

@main_bp.route('/api/trip/<int:trip_id>/chat-sync', methods=['POST'])
@login_required
def sync_trip_chat(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    chat = data.get('chat', [])
    if not isinstance(chat, list):
        return jsonify({"success": False, "error": "Invalid chat payload"}), 400

    try:
        parsed = json.loads(trip.itinerary_text) if trip.itinerary_text else {}
    except Exception:
        parsed = {}

    if isinstance(parsed, list):
        parsed = {"schema_version": 2, "itinerary": parsed}
    if not isinstance(parsed, dict):
        parsed = {"schema_version": 2}

    parsed["chat"] = chat
    trip.itinerary_text = json.dumps(parsed)
    db.session.commit()
    return jsonify({"success": True})


@main_bp.route('/api/trip/<int:trip_id>/update', methods=['POST'])
@login_required
def update_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    destination = (data.get('destination') or '').strip()
    start_date_raw = (data.get('start_date') or '').strip()
    end_date_raw = (data.get('end_date') or '').strip()
    budget = (data.get('budget') or '').strip()
    adults_raw = data.get('adults', None)
    children_raw = data.get('children', None)
    interests = (data.get('interests') or '').strip()

    if not destination:
        return jsonify({"success": False, "error": "Destination is required"}), 400
    if not start_date_raw or not end_date_raw:
        return jsonify({"success": False, "error": "Start and end dates are required"}), 400

    try:
        start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if end_date < start_date:
        return jsonify({"success": False, "error": "End date cannot be before start date"}), 400

    adults = None
    children = None
    if adults_raw is not None:
        try:
            adults = max(1, int(adults_raw))
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Adults must be a valid number"}), 400
    if children_raw is not None:
        try:
            children = max(0, int(children_raw))
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Children must be a valid number"}), 400

    trip.destination = destination[:100]
    trip.start_date = start_date
    trip.end_date = end_date
    trip.budget = budget[:50] if budget else None
    trip.interests = interests[:500] if interests else None

    # Keep the saved payload metadata in sync with edited details.
    try:
        parsed = json.loads(trip.itinerary_text) if trip.itinerary_text else {}
    except Exception:
        parsed = {}
    if isinstance(parsed, list):
        parsed = {"schema_version": 2, "itinerary": parsed}
    if isinstance(parsed, dict):
        parsed["destination"] = trip.destination
        parsed["start_date"] = trip.start_date.isoformat()
        parsed["end_date"] = trip.end_date.isoformat()
        if trip.budget:
            parsed["budget"] = trip.budget
        if trip.interests:
            parsed["interests"] = trip.interests
        if adults is not None:
            parsed["adults"] = adults
        if children is not None:
            parsed["children"] = children
        trip.itinerary_text = json.dumps(parsed)

    db.session.commit()
    return jsonify({
        "success": True,
        "trip": {
            "id": trip.id,
            "destination": trip.destination,
            "start_date": trip.start_date.isoformat(),
            "end_date": trip.end_date.isoformat(),
            "budget": trip.budget or "",
            "adults": adults,
            "children": children,
            "interests": trip.interests or ""
        }
    })

@main_bp.route('/profile')
@login_required
def profile():
    # Redirect to landing page - profile is only available as popup
    return redirect(url_for('main.landing'))

@main_bp.route('/profile/embed')
@login_required
def profile_embed():
    # Profile embed mode for popup
    today = datetime.now().date()
    trip_count = len(current_user.trips)
    saved_count = len(current_user.saved_destinations)
    saved_destinations = current_user.saved_destinations
    user_prefs = _get_user_preferences(current_user).get('categories', [])

    all_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).all()
    upcoming_trips = [t for t in all_trips if t.start_date > today]
    past_trips = [t for t in all_trips if t.end_date < today]

    all_saved = SavedDestination.query.filter_by(user_id=current_user.id).order_by(SavedDestination.created_at.desc()).all()
    recent_saved = all_saved[:2]

    explored_trips_raw = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.created_at.desc()).all()

    recent_explore_items = []
    for s in all_saved:
        recent_explore_items.append({
            "kind": "destination", "id": s.id, "title": s.name,
            "subtitle": s.tag or "Saved Destination",
            "image": s.image_url or "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop",
            "created_at": s.created_at,
            "url": url_for('main.destination_info', name=s.name)
        })
    for t in explored_trips_raw[:2]:
        img_url = "https://images.unsplash.com/photo-1548013146-72479768bbaa?auto=format&fit=crop&q=80&w=2000"
        try:
            if t.itinerary_text:
                plan = json.loads(t.itinerary_text)
                if plan.get('hero_image'):
                    img_url = plan['hero_image']
        except Exception:
            pass
        recent_explore_items.append({
            "kind": "trip", "id": t.id, "title": t.destination,
            "subtitle": "Trip Plan", "image": img_url,
            "created_at": t.created_at,
            "url": url_for('main.view_trip', trip_id=t.id)
        })
    recent_explore_items.sort(key=lambda item: item.get("created_at") or datetime.min, reverse=True)
    recent_explore_list = recent_explore_items[:4]

    trips_data = []
    for t in all_trips:
        trips_data.append({
            'id': t.id, 'destination': t.destination,
            'start_date': t.start_date.isoformat(),
            'end_date': t.end_date.isoformat(),
            'budget': t.budget
        })

    notification_settings = _get_notification_settings(current_user)
    ai_assistant_settings = _get_ai_assistant_settings(current_user)

    return render_template('profile.html',
                           today=today,
                           trip_count=trip_count,
                           saved_count=saved_count,
                           saved_destinations=saved_destinations,
                           user_prefs=user_prefs,
                           upcoming_trips=upcoming_trips,
                           past_trips=past_trips,
                           all_trips=all_trips,
                           recent_saved=recent_saved,
                           all_saved=all_saved,
                           recent_explore_list=recent_explore_list,
                           show_saved_all=False,
                           show_explored_all=False,
                           all_trips_js=trips_data,
                           notification_settings=notification_settings,
                           ai_assistant_settings=ai_assistant_settings)

@main_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    name = (request.form.get('name') or '').strip()
    phone = (request.form.get('phone') or '').strip()
    city = (request.form.get('city') or '').strip()

    # Process preferences
    raw_preferences = request.form.getlist('preferences')
    preferences = []
    seen = set()
    for pref in raw_preferences:
        cleaned = str(pref).strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            preferences.append(cleaned[:50])

    current_user.name = name
    current_user.phone = phone or None
    current_user.city = city or None

    # Keep existing non-category preferences if any, but replace categories
    existing_prefs = _get_user_preferences(current_user)
    existing_prefs['categories'] = preferences
    current_user.preferences = existing_prefs

    db.session.commit()

    # Check if this is an iframe submission (from profile popup)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('iframe_submit'):
        return jsonify({'success': True, 'message': 'Profile updated successfully!'})

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.landing'))


@main_bp.route('/profile/image/upload', methods=['POST'])
@login_required
def upload_profile_image():
    file = request.files.get('profile_image')
    if not file or not file.filename:
        flash('Please select an image file to upload.', 'error')
        if request.form.get('iframe_submit'):
            return jsonify({'success': False, 'message': 'Please select an image file to upload.'})
        return redirect(url_for('main.landing'))

    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    content_type = (file.mimetype or '').lower()
    if extension not in ALLOWED_PROFILE_IMAGE_EXTENSIONS and not content_type.startswith('image/'):
        flash('Unsupported file type. Please upload an image.', 'error')
        if request.form.get('iframe_submit'):
            return jsonify({'success': False, 'message': 'Unsupported file type. Please upload an image.'})
        return redirect(url_for('main.landing'))

    upload_dir = os.path.join(current_app.static_folder, PROFILE_UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    unique_name = f"user_{current_user.id}_{uuid4().hex}.{extension or 'jpg'}"
    save_path = os.path.join(upload_dir, unique_name)
    file.save(save_path)

    old_image_url = current_user.image_url
    current_user.image_url = url_for('static', filename=f"{PROFILE_UPLOAD_DIR.replace(os.sep, '/')}/{unique_name}")
    db.session.commit()
    _delete_local_profile_image(old_image_url)

    if request.form.get('iframe_submit'):
        return jsonify({'success': True, 'message': 'Profile image updated successfully.'})

    flash('Profile image updated successfully.', 'success')
    return redirect(url_for('main.landing'))


@main_bp.route('/profile/image/delete', methods=['POST'])
@login_required
def delete_profile_image():
    old_image_url = current_user.image_url
    if old_image_url:
        current_user.image_url = None
        db.session.commit()
        _delete_local_profile_image(old_image_url)
        if request.form.get('iframe_submit'):
            return jsonify({'success': True, 'message': 'Profile image deleted.'})
        flash('Profile image deleted.', 'success')
    else:
        if request.form.get('iframe_submit'):
            return jsonify({'success': False, 'message': 'No profile image found.'})
        flash('No profile image found.', 'info')
    return redirect(url_for('main.landing'))

@main_bp.route('/calendar')
@login_required
def calendar():
    return redirect(url_for('main.landing'))

@main_bp.route('/settings')
@login_required
def settings():
    return redirect(url_for('main.landing'))


@main_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    updated = {
        'notifications_enabled': request.form.get('notifications_enabled', 'on') == 'on',
        'trip_alerts': bool(request.form.get('trip_alerts')),
        'ai_suggestions': bool(request.form.get('ai_suggestions')),
        'system_notifications': bool(request.form.get('system_notifications')),
        'seasonal_recommendations': bool(request.form.get('seasonal_recommendations')),
        'email_notifications': bool(request.form.get('email_notifications'))
    }
    _set_user_notification_settings(current_user, updated)
    db.session.commit()

    # Check if this is an iframe submission (from profile popup)
    if request.form.get('iframe_submit'):
        return jsonify({'success': True, 'message': 'Notification settings updated successfully.'})

    flash('Notification settings updated successfully.', 'success')
    return redirect(url_for('main.landing'))


@main_bp.route('/settings/ai-assistant', methods=['POST'])
@login_required
def update_ai_assistant_settings():
    from models import ChatSession
    old_settings = _get_ai_assistant_settings(current_user)
    updated = {
        'proactive_tips': bool(request.form.get('proactive_tips')),
        'chat_history': bool(request.form.get('chat_history'))
    }
    _set_ai_assistant_settings(current_user, updated)

    chat_history_cleared = False
    if old_settings.get('chat_history', True) and not updated['chat_history']:
        ChatSession.query.filter_by(user_id=current_user.id).delete()
        chat_history_cleared = True
        message = 'AI assistant settings updated. Existing chat history has been cleared.'
    else:
        message = 'AI assistant settings updated successfully.'

    db.session.commit()

    wants_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
        'application/json' in (request.headers.get('Accept') or '')
    if wants_json:
        return jsonify({
            'success': True,
            'message': message,
            'settings': updated,
            'chat_history_cleared': chat_history_cleared
        })

    if chat_history_cleared:
        flash('AI assistant settings updated. Existing chat history has been cleared.', 'success')
    else:
        flash('AI assistant settings updated successfully.', 'success')

    return redirect(url_for('main.landing'))

@main_bp.route('/profile-ai')
@login_required
def profile_ai():
    return redirect(url_for('main.landing'))

@main_bp.route('/api/explore-destinations')
@login_required
def api_explore_destinations():
    state = (request.args.get('state') or '').strip()
    if state == "Select State":
        state = ''

    category = (request.args.get('category') or '').strip()
    search_query = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)

    # No filters selected: return empty result so initial explore UI can stay in welcome state.
    if not state and not category and not search_query:
        return jsonify({'destinations': [], 'total_count': 0, 'state': '', 'category': 'All'})
    
    # If no category selected, auto-apply user's saved travel preferences from profile
    auto_applied_prefs = False
    if not category and (state or search_query):
        user_prefs = _get_user_preferences(current_user)
        prefs_categories = user_prefs.get('categories', [])
        if prefs_categories:
            category = ','.join(prefs_categories)
            auto_applied_prefs = True
    
    data = AIService.explore_destinations(
        state=state if state else None,
        category=category if category else None,
        search_query=search_query if search_query else None,
        page=page
    )
    data = _sanitize_destination_payload_icons(data)
    data['auto_applied_prefs'] = auto_applied_prefs
    return jsonify(data)

@main_bp.route('/api/destination-attractions')
@login_required
def api_destination_attractions():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_attractions(name)
    data = _sanitize_destination_payload_icons(data)
    _track_activity(current_user, name, 'attractions_view')
    return jsonify(_fallback_response(data, "Live attraction intelligence is unavailable. Showing fallback data."))

@main_bp.route('/api/destination-itinerary')
@login_required
def api_destination_itinerary():
    name = request.args.get('name', '')
    days = request.args.get('days', 3, type=int)
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_itinerary(name, days=days)
    data = _sanitize_destination_payload_icons(data)
    _track_activity(current_user, name, 'itinerary_view')
    return jsonify(_fallback_response(data, "Live itinerary generation is unavailable. Showing fallback itinerary shell."))

@main_bp.route('/api/destination-gallery')
@login_required
def api_destination_gallery():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_gallery(name)
    data = _fallback_response(data, "Gallery search is unavailable. Showing fallback media where possible.")
    if isinstance(data, dict) and not data.get("fallback"):
        if not isinstance(data.get("images"), list) or len(data.get("images", [])) == 0:
            data = _mark_fallback(data, "Gallery provider returned no results. Fallback media mode is active.", True)
    _track_activity(current_user, name, 'gallery_view')
    return jsonify(data)

@main_bp.route('/api/destination-hero')
@login_required
def api_destination_hero():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_hero_image(name)
    data = _fallback_response(data, "Hero image service is unavailable. Showing fallback image.")
    if isinstance(data, dict) and (data.get("success") is False):
        data = _mark_fallback(data, "Hero image provider is degraded. Using fallback hero image.", True)
    _track_activity(current_user, name, 'hero_view')
    return jsonify(data)


@main_bp.route('/api/save-destination', methods=['POST'])
@login_required
def save_destination():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"success": False, "error": "Name required"}), 400
    
    # Check if already saved
    existing = SavedDestination.query.filter_by(user_id=current_user.id, name=name).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        _track_activity(current_user, name, 'unsave')
        return jsonify({"success": True, "saved": False})
    
    new_save = SavedDestination(
        user_id=current_user.id,
        name=name,
        description=data.get('description'),
        tag=data.get('tag'),
        icon=data.get('icon'),
        image_url=data.get('image_url')
    )
    db.session.add(new_save)
    db.session.commit()
    _track_activity(current_user, name, 'save')
    return jsonify({"success": True, "saved": True})

@main_bp.route('/api/unsave-destination', methods=['POST'])
@login_required
def unsave_destination():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    save_id = data.get('id')

    target = None
    if isinstance(save_id, int):
        target = SavedDestination.query.filter_by(user_id=current_user.id, id=save_id).first()
    if not target and name:
        target = SavedDestination.query.filter_by(user_id=current_user.id, name=name).first()

    if not target:
        return jsonify({"success": False, "error": "Saved destination not found"}), 404

    db.session.delete(target)
    db.session.commit()
    _track_activity(current_user, name or target.name, 'unsave')
    return jsonify({"success": True})

@main_bp.route('/api/check-saved')
@login_required
def check_saved():
    name = request.args.get('name')
    if not name:
        return jsonify({"saved": False})
    saved = SavedDestination.query.filter_by(user_id=current_user.id, name=name).first()
    return jsonify({"saved": bool(saved)})

@main_bp.route('/api/favorite-destination', methods=['POST'])
@login_required
def favorite_destination():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"success": False, "error": "Name required"}), 400

    existing = FavoriteDestination.query.filter_by(user_id=current_user.id, name=name).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        _track_activity(current_user, name, 'unfavorite')
        return jsonify({"success": True, "favorited": False})

    new_fav = FavoriteDestination(
        user_id=current_user.id,
        name=name[:100],
        description=data.get('description'),
        tag=data.get('tag'),
        icon=data.get('icon'),
        image_url=data.get('image_url')
    )
    db.session.add(new_fav)
    db.session.commit()
    _track_activity(current_user, name, 'favorite')
    return jsonify({"success": True, "favorited": True})

@main_bp.route('/api/unfavorite-destination', methods=['POST'])
@login_required
def unfavorite_destination():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    fav_id = data.get('id')

    target = None
    if isinstance(fav_id, int):
        target = FavoriteDestination.query.filter_by(user_id=current_user.id, id=fav_id).first()
    if not target and name:
        target = FavoriteDestination.query.filter_by(user_id=current_user.id, name=name).first()

    if not target:
        return jsonify({"success": False, "error": "Favorite destination not found"}), 404

    db.session.delete(target)
    db.session.commit()
    _track_activity(current_user, name or target.name, 'unfavorite')
    return jsonify({"success": True})

@main_bp.route('/api/check-favorite')
@login_required
def check_favorite():
    name = request.args.get('name')
    if not name:
        return jsonify({"favorited": False})
    favorite = FavoriteDestination.query.filter_by(user_id=current_user.id, name=name).first()
    return jsonify({"favorited": bool(favorite)})

@main_bp.route('/api/get-destination-story')
@login_required
def get_destination_story():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name required"}), 400
    story_data = AIService.generate_destination_story(name)
    _track_activity(current_user, name, 'story_view')
    return jsonify(_fallback_response(story_data, "Story generator is unavailable. Please try again shortly."))

@main_bp.route('/api/get-story-voice')
@login_required
def get_story_voice():
    text = request.args.get('text', '')
    if not text:
        return jsonify({"error": "Text required"}), 400
    
    try:
        import asyncio
        import io
        import os
        import tempfile
        from flask import send_file
        import edge_tts

        # Limit payload size for reliable TTS generation
        tts_text = text.strip()[:5000]
        if not tts_text:
            return jsonify({"error": "Text required"}), 400

        # Use a natural-sounding neural voice (global default)
        voice = request.args.get('voice', 'en-US-GuyNeural')
        rate = request.args.get('rate', '+0%')

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name

        try:
            communicate = edge_tts.Communicate(tts_text, voice=voice, rate=rate)
            asyncio.run(communicate.save(tmp_path))

            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return send_file(io.BytesIO(audio_bytes), mimetype='audio/mpeg')
    except Exception as edge_err:
        # Fallback to gTTS if neural service/dependency is unavailable
        try:
            from gtts import gTTS
            import io
            from flask import send_file
            tts = gTTS(text=text[:5000], lang='en', tld='com', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return send_file(fp, mimetype='audio/mpeg')
        except Exception as e:
            print(f"TTS Error (edge={edge_err}): {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/destination-weather')
@login_required
def api_destination_weather():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Destination name is required"}), 400
    weather = WeatherService.get_forecast(name)
    if not weather:
        return jsonify({
            "available": False,
            "source": "fallback",
            "city": name,
            "temperature": None,
            "description": "Weather data unavailable right now",
            "humidity": None,
            "wind_speed": None,
            "forecast": []
        }), 200
    return jsonify(weather)

@main_bp.route('/api/destination-chat', methods=['POST'])
@login_required
def api_destination_chat():
    body = request.get_json()
    destination = body.get('destination', '')
    message = body.get('message', '')
    history = body.get('history', [])
    
    if not destination or not message:
        return jsonify({"error": "Destination and message required"}), 400
    
    try:
        from groq import Groq
        from config import Config
        client = Groq(api_key=Config.GROQ_API_KEY)
        
        system_prompt = f"""You are Skupheon AI, an expert travel guide for {destination}. 
You are knowledgeable about:
- Local attractions, hidden gems, and must-visit places
- Best restaurants, street food, and local cuisine
- Culture, history, and traditions
- Travel tips, safety, transportation, and accommodation
- Best times to visit, weather, and seasonal activities
- Budget tips and itinerary suggestions

Be warm, conversational, and helpful. Use emojis sparingly for friendliness.
Keep responses concise but informative (2-4 paragraphs max).
If asked about something unrelated to travel or {destination}, gently redirect to travel topics."""
        
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-10:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1024
        )
        
        reply = completion.choices[0].message.content
        _track_activity(current_user, destination, 'chat', {'message_count': len(history) + 1})
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"reply": f"I'm having trouble connecting right now. Please try again in a moment! 🙏"}), 200

@main_bp.route('/api/optimize-route', methods=['POST'])
@login_required
def api_optimize_route():
    data = request.get_json()
    items = data.get('items', [])
    if not items:
        return jsonify({"error": "Items required"}), 400
    
    optimized = []
    # If the user sends all days, we might want to optimize per day
    # But usually this is called for a single day's activities
    from services import GraphService
    optimized = GraphService.optimize_route(items)
    return jsonify({"optimized": optimized})
@main_bp.route('/api/general-chat', methods=['POST'])
@login_required
def api_general_chat():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    response = AIService.generate_chat_response(message)
    if isinstance(response, dict):
        # Keep compatibility with old clients (`reply`) and current client (`response`, `images`).
        out = {
            "reply": response.get("response", ""),
            "response": response.get("response", ""),
            "images": response.get("images", []),
            "data": response.get("data", {}),
            "fallback": bool(response.get("error")),
            "fallback_message": "Chat AI is currently degraded. You are seeing fallback output." if response.get("error") else ""
        }
        return jsonify(out)
    return jsonify({"reply": str(response), "response": str(response), "images": [], "data": {}, "fallback": False, "fallback_message": ""})


@main_bp.route('/api/save-itinerary', methods=['POST'])
@login_required
def save_itinerary():
    try:
        data = request.json
        destination = data.get('destination', 'Magic Trip')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        budget = data.get('budget', 'Medium')
        adults = data.get('adults', 2)
        children = data.get('children', 0)
        interests = data.get('interests', 'General')
        itinerary = data.get('itinerary', [])
        weather = data.get('weather', {})
        chat = data.get('chat', [])

        from datetime import datetime, timedelta

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = datetime.now().date()
        else:
            start_date = datetime.now().date()

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = start_date + timedelta(days=4)
        else:
            end_date = start_date + timedelta(days=4)

        try:
            adults = max(1, int(adults))
        except (TypeError, ValueError):
            adults = 2
        try:
            children = max(0, int(children))
        except (TypeError, ValueError):
            children = 0

        saved_payload = {
            "schema_version": 2,
            "destination": destination,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "budget": budget,
            "adults": adults,
            "children": children,
            "interests": interests,
            "itinerary": itinerary if isinstance(itinerary, list) else [],
            "weather": weather if isinstance(weather, dict) else {},
            "chat": chat if isinstance(chat, list) else []
        }

        trip = Trip(
            user_id=current_user.id,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            interests=interests,
            itinerary_text=json.dumps(saved_payload)
        )
        db.session.add(trip)
        _track_activity(current_user, destination, 'trip_create', {'budget': budget, 'adults': adults, 'children': children})
        
        created_notifications = []
        notif_settings = _get_notification_settings(current_user)
        if notif_settings.get('notifications_enabled', True) and notif_settings.get('trip_alerts', True):
            display_name = _notification_display_name(current_user)
            created_notifications.append(_create_notification(
                current_user,
                f"Nice one, {display_name}! Your trip to {destination} has been saved and is ready whenever you are.",
                'success',
                f"Trip Saved: {destination}"
            ))
        
        db.session.commit()
        _send_created_notification_emails(current_user, created_notifications)
        return jsonify({"success": True, "trip_id": trip.id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@main_bp.route('/api/add-destination-to-calendar', methods=['POST'])
@login_required
def add_destination_to_calendar():
    try:
        data = request.get_json(silent=True) or {}
        destination = (data.get('destination') or '').strip()
        itinerary_days = data.get('days') if isinstance(data.get('days'), list) else []

        if not destination:
            return jsonify({"success": False, "error": "Destination is required."}), 400

        start_date = datetime.now().date()
        total_days = max(1, len(itinerary_days))
        end_date = start_date + timedelta(days=total_days - 1)

        saved_payload = {
            "schema_version": 2,
            "source": "destination_itinerary_add_to_calendar",
            "added_at": datetime.utcnow().isoformat() + "Z",
            "destination": destination,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "itinerary": itinerary_days
        }

        trip = Trip(
            user_id=current_user.id,
            destination=destination[:100],
            start_date=start_date,
            end_date=end_date,
            budget="Destination Itinerary",
            interests="Added from destination page",
            itinerary_text=json.dumps(saved_payload)
        )
        db.session.add(trip)

        created_notifications = []
        notif_settings = _get_notification_settings(current_user)
        if notif_settings.get('notifications_enabled', True) and notif_settings.get('trip_alerts', True):
            display_name = _notification_display_name(current_user)
            created_notifications.append(_create_notification(
                current_user,
                f"{display_name}, {destination} was added to your calendar.",
                'success',
                f"Trip Added: {destination}"
            ))

        db.session.commit()
        _track_activity(current_user, destination, 'trip_create', {'source': 'add_to_calendar'})
        _send_created_notification_emails(current_user, created_notifications)
        return jsonify({"success": True, "trip_id": trip.id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main_bp.route('/api/trip/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    db.session.delete(trip)
    db.session.commit()
    return jsonify({"success": True})

@main_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notif_settings = _get_notification_settings(current_user)
    if not notif_settings.get('notifications_enabled', True):
        return jsonify({
            'notifications': [],
            'unread_count': 0
        })
    should_generate = (request.args.get('generate', '1') != '0')
    if should_generate:
        _generate_smart_notifications(current_user)
    _send_pending_notification_emails(current_user)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    notifs_data = []
    for n in notifications:
        created_utc = n.created_at.replace(tzinfo=timezone.utc) if n.created_at else None
        notifs_data.append({
            'id': n.id,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %Y %H:%M') if n.created_at else '',
            'created_at_iso': created_utc.isoformat() if created_utc else None
        })
    
    return jsonify({
        'notifications': notifs_data,
        'unread_count': unread_count
    })


@main_bp.route('/api/notifications/generate', methods=['POST'])
@login_required
def generate_notifications_now():
    created_count = _generate_smart_notifications(current_user, force=True)
    return jsonify({'success': True, 'created': created_count})

@main_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({
        Notification.is_read: True,
        Notification.updated_at: datetime.utcnow()
    })
    db.session.commit()
    return jsonify({'success': True})

# --- Chat Assistant API ---

@main_bp.route('/api/chat/sessions', methods=['GET'])
@login_required
def get_chat_sessions():
    if not _get_ai_assistant_settings(current_user).get('chat_history', True):
        return jsonify([])
    from models import ChatSession
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).all()
    pinned_ids = set(_get_pinned_chat_session_ids(current_user))
    sessions_data = []
    for s in sessions:
        last_msg = ""
        if s.messages:
            last_msg = s.messages[-1].content[:60] + "..." if len(s.messages[-1].content) > 60 else s.messages[-1].content
        
        sessions_data.append({
            'id': s.id,
            'title': s.title or "New Conversation",
            'last_message': last_msg,
            'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at_ts': s.updated_at.timestamp() if s.updated_at else 0,
            'pinned': s.id in pinned_ids
        })
    sessions_data.sort(key=lambda x: (not x['pinned'], -x['updated_at_ts']))
    for s in sessions_data:
        s.pop('updated_at_ts', None)
    return jsonify(sessions_data)

@main_bp.route('/api/chat/session/<int:session_id>', methods=['GET'])
@login_required
def get_chat_messages(session_id):
    if not _get_ai_assistant_settings(current_user).get('chat_history', True):
        return jsonify([])
    from models import ChatSession
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    messages_data = []
    for m in session.messages:
        messages_data.append({
            'role': m.role,
            'content': m.content,
            'created_at': m.created_at.strftime('%H:%M')
        })
    return jsonify(messages_data)

@main_bp.route('/api/chat/session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_chat_session(session_id):
    from models import ChatSession
    if not _get_ai_assistant_settings(current_user).get('chat_history', True):
        return jsonify({"error": "Chat history is disabled"}), 400

    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    pinned_ids = set(_get_pinned_chat_session_ids(current_user))
    if session.id in pinned_ids:
        pinned_ids.remove(session.id)
        _set_pinned_chat_session_ids(current_user, list(pinned_ids))

    db.session.delete(session)
    db.session.commit()
    return jsonify({"success": True})

@main_bp.route('/api/chat/sessions/clear', methods=['POST'])
@login_required
def clear_chat_sessions():
    from models import ChatSession
    if not _get_ai_assistant_settings(current_user).get('chat_history', True):
        return jsonify({"error": "Chat history is disabled"}), 400

    ChatSession.query.filter_by(user_id=current_user.id).delete()
    _set_pinned_chat_session_ids(current_user, [])
    db.session.commit()
    return jsonify({"success": True})


@main_bp.route('/api/chat/session/<int:session_id>/title', methods=['PATCH'])
@login_required
def rename_chat_session(session_id):
    from models import ChatSession
    if not _get_ai_assistant_settings(current_user).get('chat_history', True):
        return jsonify({"error": "Chat history is disabled"}), 400

    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    session.title = title[:150]
    db.session.commit()
    return jsonify({"success": True, "title": session.title})


@main_bp.route('/api/chat/session/<int:session_id>/pin', methods=['POST'])
@login_required
def toggle_pin_chat_session(session_id):
    from models import ChatSession
    if not _get_ai_assistant_settings(current_user).get('chat_history', True):
        return jsonify({"error": "Chat history is disabled"}), 400

    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    requested_pin = data.get('pinned', None)
    pinned_ids = set(_get_pinned_chat_session_ids(current_user))
    is_currently_pinned = session.id in pinned_ids
    should_pin = (not is_currently_pinned) if requested_pin is None else bool(requested_pin)

    if should_pin:
        pinned_ids.add(session.id)
    else:
        pinned_ids.discard(session.id)

    _set_pinned_chat_session_ids(current_user, list(pinned_ids))
    db.session.commit()
    return jsonify({"success": True, "pinned": should_pin})

@main_bp.route('/api/my-trip-context', methods=['GET'])
@login_required
def get_my_trip_context():
    """Fetch the user's saved trips and saved destinations for AI assistant context."""
    today = datetime.now().date()

    # Fetch all trips for the user
    all_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    trips_data = []
    for t in all_trips:
        trip_info = {
            'id': t.id,
            'destination': t.destination,
            'start_date': t.start_date.isoformat() if t.start_date else None,
            'end_date': t.end_date.isoformat() if t.end_date else None,
            'budget': t.budget,
            'interests': t.interests,
            'status': 'upcoming' if t.start_date and t.start_date > today else ('ongoing' if t.start_date and t.end_date and t.start_date <= today <= t.end_date else 'completed'),
        }
        # Parse itinerary for summary
        try:
            parsed = json.loads(t.itinerary_text) if t.itinerary_text else {}
            if isinstance(parsed, dict):
                trip_info['adults'] = parsed.get('adults')
                trip_info['children'] = parsed.get('children')
                itinerary_days = parsed.get('itinerary', [])
                if isinstance(itinerary_days, list) and itinerary_days:
                    trip_info['day_count'] = len(itinerary_days)
                    # Extract a brief summary of activities
                    activities_summary = []
                    for day in itinerary_days[:3]:
                        if isinstance(day, dict):
                            day_title = day.get('title', day.get('day_title', ''))
                            if day_title:
                                activities_summary.append(day_title)
                    if activities_summary:
                        trip_info['highlights'] = activities_summary
        except Exception:
            pass
        trips_data.append(trip_info)

    # Fetch saved destinations
    saved = SavedDestination.query.filter_by(user_id=current_user.id).order_by(SavedDestination.created_at.desc()).all()
    saved_data = []
    for s in saved:
        saved_data.append({
            'name': s.name,
            'description': s.description,
            'tag': s.tag,
        })

    # Fetch favorite destinations
    favs = FavoriteDestination.query.filter_by(user_id=current_user.id).order_by(FavoriteDestination.created_at.desc()).all()
    favs_data = []
    for f in favs:
        favs_data.append({
            'name': f.name,
            'description': f.description,
            'tag': f.tag,
        })

    return jsonify({
        'trips': trips_data,
        'saved_destinations': saved_data,
        'favorite_destinations': favs_data,
    })


@main_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    from models import ChatSession, ChatMessage
    ai_settings = _get_ai_assistant_settings(current_user)
    chat_history_enabled = ai_settings.get('chat_history', True)
    data = request.json
    message_text = data.get('message')
    session_id = data.get('session_id')
    image_base64 = data.get('image_base64')
    image_mime = data.get('image_mime') or 'image/jpeg'
    image_name = (data.get('image_name') or 'image').strip()
    my_trip_connected = data.get('my_trip_connected', False)
    my_trip_scope = data.get('my_trip_scope')  # 'trips' | 'destinations' | None
    
    if not message_text and not image_base64:
        return jsonify({"error": "Message or image required"}), 400
    
    # Build My Trip context string if connected
    my_trip_context_str = ""
    if my_trip_connected:
        my_trip_context_str = _build_my_trip_context_for_ai(current_user, scope=my_trip_scope)
    
    if not chat_history_enabled:
        if image_base64:
            try:
                image_bytes = base64.b64decode(image_base64)
            except Exception:
                return jsonify({"error": "Invalid image payload"}), 400
            ai_response_text = AIService.analyze_image_for_travel(image_bytes, image_mime, message_text)
        else:
            ai_response_text = AIService.general_chat(message_text, history=[], my_trip_context=my_trip_context_str)
        return jsonify({
            'session_id': None,
            'response': ai_response_text,
            'created_at': datetime.utcnow().strftime('%H:%M')
        })

    # Get or create session
    if session_id:
        session = ChatSession.query.get(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({"error": "Invalid session"}), 403
    else:
        # Create new session
        first_title = message_text or f"Image: {image_name}"
        session = ChatSession(user_id=current_user.id, title=first_title[:30] + "..." if len(first_title) > 30 else first_title)
        db.session.add(session)
        db.session.commit()
    
    # Save user message
    if image_base64:
        user_content = (message_text + "\n" if message_text else "") + f"[Image attached: {image_name}]"
    else:
        user_content = message_text
    user_msg = ChatMessage(session_id=session.id, role='user', content=user_content)
    db.session.add(user_msg)
    
    # Prepare history for AI
    history = []
    past_messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()
    for m in past_messages:
        history.append({'role': m.role, 'content': m.content})
    
    # Get AI response
    if image_base64:
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            return jsonify({"error": "Invalid image payload"}), 400
        ai_response_text = AIService.analyze_image_for_travel(image_bytes, image_mime, message_text)
    else:
        ai_response_text = AIService.general_chat(message_text, history=history[:-1], my_trip_context=my_trip_context_str)
    
    # Save AI message
    ai_msg = ChatMessage(session_id=session.id, role='ai', content=ai_response_text)
    db.session.add(ai_msg)
    
    # Update session's updated_at
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'session_id': session.id,
        'response': ai_response_text,
        'created_at': ai_msg.created_at.strftime('%H:%M')
    })


def _build_my_trip_context_for_ai(user, scope=None):
    """Build a context string from the user's trips and saved destinations for the AI system prompt.
    scope: 'trips' | 'destinations' | None (None = all data)
    """
    today = datetime.now().date()
    lines = []

    # Trips (Plan a Trip)
    if scope is None or scope == 'trips':
        trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.start_date.desc()).limit(15).all()
        if trips:
            lines.append("=== USER'S SAVED TRIPS (Plan a Trip) ===")
            for t in trips:
                status = 'upcoming' if t.start_date and t.start_date > today else ('ongoing' if t.start_date and t.end_date and t.start_date <= today <= t.end_date else 'completed')
                trip_line = f"- {t.destination} | {t.start_date.isoformat() if t.start_date else 'N/A'} to {t.end_date.isoformat() if t.end_date else 'N/A'} | Budget: {t.budget or 'N/A'} | Status: {status}"
                if t.interests:
                    trip_line += f" | Interests: {t.interests}"
                try:
                    parsed = json.loads(t.itinerary_text) if t.itinerary_text else {}
                    if isinstance(parsed, dict):
                        adults = parsed.get('adults')
                        children = parsed.get('children')
                        if adults or children:
                            trip_line += f" | Travelers: {adults or 'N/A'} adults, {children or 0} children"
                except Exception:
                    pass
                lines.append(trip_line)

    # Saved destinations (Explore Destination)
    if scope is None or scope == 'destinations':
        saved = SavedDestination.query.filter_by(user_id=user.id).order_by(SavedDestination.created_at.desc()).limit(20).all()
        if saved:
            lines.append("\n=== USER'S SAVED DESTINATIONS (Explore Destination) ===")
            for s in saved:
                dest_line = f"- {s.name}"
                if s.tag:
                    dest_line += f" | Tag: {s.tag}"
                if s.description:
                    desc_short = s.description[:120] + "..." if len(s.description or '') > 120 else s.description
                    dest_line += f" | {desc_short}"
                lines.append(dest_line)

        favs = FavoriteDestination.query.filter_by(user_id=user.id).order_by(FavoriteDestination.created_at.desc()).limit(15).all()
        if favs:
            lines.append("\n=== USER'S FAVORITE DESTINATIONS ===")
            for f in favs:
                fav_line = f"- {f.name}"
                if f.tag:
                    fav_line += f" | Tag: {f.tag}"
                lines.append(fav_line)

    if not lines:
        if scope == 'trips':
            return "The user has no saved trips (Plan a Trip) yet."
        elif scope == 'destinations':
            return "The user has no saved or favorite destinations (Explore Destination) yet."
        return ""

    return "\n".join(lines)

@main_bp.route('/about')
@login_required
def about():
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        subject_key = (request.form.get('subject') or '').strip()
        trip_reference = (request.form.get('trip_reference') or '').strip()
        message_text = (request.form.get('message') or '').strip()
        consent = request.form.get('consent')

        if not all([name, email, subject_key, message_text]) or not consent:
            flash('Please complete all required fields and provide consent.', 'danger')
            return redirect(url_for('main.contact'))

        subject_labels = {
            'general': 'General Inquiry',
            'support': 'Technical Support',
            'feedback': 'Feedback & Suggestions',
            'partnership': 'Business Partnership',
            'report': 'Report an Issue',
            'other': 'Other'
        }
        subject_label = subject_labels.get(subject_key, 'General Inquiry')
        admin_recipient = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')

        if not admin_recipient:
            flash('Contact email is not configured yet. Please try again shortly.', 'danger')
            return redirect(url_for('main.contact'))

        try:
            try:
                submitted_dt = datetime.utcnow()
                submitted_on = submitted_dt.strftime("%d %b %Y, %I:%M %p UTC")
            except Exception:
                submitted_dt = datetime.utcnow()
                submitted_on = submitted_dt.strftime("%d %b %Y, %I:%M %p UTC")

            logo_cid = None
            logo_path = os.path.join(current_app.root_path, 'static', 'img', 'logo.png')

            admin_msg = Message(
                subject=f"[RoutheonSkups Contact] {subject_label} - {name}",
                recipients=[admin_recipient],
                reply_to=email
            )
            esc_name = html.escape(name)
            esc_email = html.escape(email)
            esc_phone = html.escape(phone or 'Not provided')
            esc_subject = html.escape(subject_label)
            esc_trip_ref = html.escape(trip_reference or 'Not provided')
            esc_message = html.escape(message_text)
            admin_msg.body = (
                "New contact form submission - RoutheonSkups\n\n"
                f"Submitted On: {submitted_on}\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone or 'Not provided'}\n"
                f"Subject: {subject_label}\n"
                f"Trip Reference: {trip_reference or 'Not provided'}\n\n"
                "Message:\n"
                f"{message_text}\n"
            )

            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as logo_file:
                    logo_data = logo_file.read()
                logo_mime = mimetypes.guess_type(logo_path)[0] or 'image/png'
                logo_cid = 'routheonskups-logo'
                admin_msg.attach(
                    filename='logo.png',
                    content_type=logo_mime,
                    data=logo_data,
                    disposition='inline',
                    headers={'Content-ID': f'<{logo_cid}>'}
                )

            logo_html = (
                f'<img src="cid:{logo_cid}" alt="RoutheonSkups Logo" style="height:42px; width:auto; display:block;">'
                if logo_cid else
                '<h2 style="margin:0; color:#ffffff; font-size:22px;">RoutheonSkups</h2>'
            )

            admin_msg.html = f"""
            <div style="font-family:'Segoe UI',Arial,sans-serif;background:#000000;padding:40px 20px;">
              <div style="max-width:560px;margin:0 auto;">
                <div style="text-align:center;margin-bottom:32px;">{logo_html}</div>
                <div style="background:#0A0A0A;border:1px solid #1A1A1A;border-radius:16px;padding:36px 32px;">
                  <h1 style="margin:0 0 8px;font-size:20px;font-weight:800;color:#FFFFFF;">New Contact Form Submission</h1>
                  <p style="margin:0 0 24px;font-size:13px;color:rgba(255,255,255,0.5);">Submitted on {submitted_on}</p>
                  <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:8px 0;color:rgba(255,255,255,0.5);width:140px;font-size:13px;"><strong>Name</strong></td><td style="padding:8px 0;color:#FFFFFF;font-size:13px;">{esc_name}</td></tr>
                    <tr><td style="padding:8px 0;color:rgba(255,255,255,0.5);font-size:13px;"><strong>Email</strong></td><td style="padding:8px 0;color:#FFFFFF;font-size:13px;">{esc_email}</td></tr>
                    <tr><td style="padding:8px 0;color:rgba(255,255,255,0.5);font-size:13px;"><strong>Phone</strong></td><td style="padding:8px 0;color:#FFFFFF;font-size:13px;">{esc_phone}</td></tr>
                    <tr><td style="padding:8px 0;color:rgba(255,255,255,0.5);font-size:13px;"><strong>Subject</strong></td><td style="padding:8px 0;color:#FFFFFF;font-size:13px;">{esc_subject}</td></tr>
                    <tr><td style="padding:8px 0;color:rgba(255,255,255,0.5);font-size:13px;"><strong>Trip Ref</strong></td><td style="padding:8px 0;color:#FFFFFF;font-size:13px;">{esc_trip_ref}</td></tr>
                  </table>
                  <div style="margin-top:18px;">
                    <p style="margin:0 0 8px;color:rgba(255,255,255,0.5);font-size:13px;"><strong>Message</strong></p>
                    <div style="background:#141414;border:1px solid #1A1A1A;border-radius:10px;padding:14px;color:rgba(255,255,255,0.8);font-size:13px;white-space:pre-wrap;">{esc_message}</div>
                  </div>
                </div>
                <p style="margin:28px 0 0;font-size:11.5px;color:rgba(255,255,255,0.4);text-align:center;">
                  <strong style="color:rgba(255,255,255,0.6);">RoutheonSkups</strong> — AI Travel Planning
                </p>
              </div>
            </div>
            """
            mail.send(admin_msg)

            user_msg = Message(
                subject="We received your message - RoutheonSkups",
                recipients=[email]
            )
            user_logo_html = '<h2 style="margin:0; color:#ffffff; font-size:22px;">RoutheonSkups</h2>'
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as logo_file:
                    logo_data = logo_file.read()
                logo_mime = mimetypes.guess_type(logo_path)[0] or 'image/png'
                user_logo_cid = 'routheonskups-logo-user'
                user_msg.attach(
                    filename='logo.png',
                    content_type=logo_mime,
                    data=logo_data,
                    disposition='inline',
                    headers={'Content-ID': f'<{user_logo_cid}>'}
                )
                user_logo_html = f'<img src="cid:{user_logo_cid}" alt="RoutheonSkups Logo" style="height:38px; width:auto; display:block;">'
            user_msg.body = (
                "Hi,\n\n"
                "Thank you for contacting RoutheonSkups. We have received your message and our team will respond soon.\n\n"
                f"Submitted On: {submitted_on}\n"
                f"Subject: {subject_label}\n\n"
                "Your message:\n"
                f"{message_text}\n\n"
                "Regards,\nRoutheonSkups Team"
            )
            user_msg.html = f"""
            <div style="font-family:'Segoe UI',Arial,sans-serif;background:#000000;padding:40px 20px;">
              <div style="max-width:480px;margin:0 auto;">
                <div style="text-align:center;margin-bottom:32px;">{user_logo_html}</div>
                <div style="background:#0A0A0A;border:1px solid #1A1A1A;border-radius:16px;padding:36px 32px;">
                  <h1 style="margin:0 0 8px;font-size:21px;font-weight:800;color:#FFFFFF;">We Received Your Message</h1>
                  <p style="margin:0 0 20px;font-size:14px;color:rgba(255,255,255,0.8);line-height:1.6;">Hi {esc_name}, thank you for contacting <strong>RoutheonSkups</strong>. Our team has received your request and will get back to you soon.</p>
                  <p style="margin:0 0 4px;font-size:13px;color:rgba(255,255,255,0.5);"><strong>Submitted On:</strong> {submitted_on}</p>
                  <p style="margin:0 0 16px;font-size:13px;color:rgba(255,255,255,0.5);"><strong>Subject:</strong> {esc_subject}</p>
                  <div style="background:#141414;border:1px solid #1A1A1A;border-radius:10px;padding:14px;color:rgba(255,255,255,0.8);font-size:13px;white-space:pre-wrap;">{esc_message}</div>
                </div>
                <p style="margin:28px 0 0;font-size:11.5px;color:rgba(255,255,255,0.4);text-align:center;">
                  <strong style="color:rgba(255,255,255,0.6);">RoutheonSkups</strong> — AI Travel Planning
                </p>
              </div>
            </div>
            """
            mail.send(user_msg)

            flash('Your message was sent successfully. A confirmation email has also been sent to your inbox.', 'success')
        except Exception as e:
            print(f"Contact form email error: {e}")
            flash('We could not send your message right now. Please try again shortly.', 'danger')

        return redirect(url_for('main.contact'))

    return render_template('contact.html')

def _csv_response(filename, headers, rows):
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    csv_content = csv_buffer.getvalue()
    csv_buffer.close()
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}_{timestamp}.csv'}
    )

@main_bp.route('/api/track-destination-click', methods=['POST'])
@login_required
def track_destination_click():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    action = (data.get('action') or 'click').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Name required'}), 400
    _track_activity(current_user, name, action, data.get('extra_data'))
    return jsonify({'success': True})

@main_bp.route('/faq')
@login_required
def faq():
    return render_template('faq.html')

@main_bp.route('/api/faq-chat', methods=['POST'])
@login_required
def faq_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({"error": "Message required"}), 400

    try:
        prompt = (
            "Answer as RoutheonSkups FAQ assistant. Keep answers short, practical, and focused on "
            "platform usage, trip planning, account help, and support queries.\n\n"
            f"User question: {message}"
        )
        response = AIService.general_chat(prompt)
        return jsonify({"response": response})
    except Exception as e:
        print(f"FAQ chat error: {e}")
        return jsonify({"response": "I am having trouble right now. Please try again shortly."}), 200


# ── Cascading Location Selection API ──────────────────────────────────────

@main_bp.route('/api/countries')
def api_countries():
    """Return all 31 supported countries with metadata."""
    from global_countries import COUNTRIES
    countries = []
    for name, data in COUNTRIES.items():
        countries.append({
            "name": name,
            "code": data["code"],
            "continent": data["continent"],
            "currency": data["currency"],
            "currency_symbol": data["currency_symbol"],
            "timezone": data["timezone"],
            "region_label": data["region_label"],
            "center": get_country_center_coords(name),
        })
    countries.sort(key=lambda c: c["name"])
    return jsonify(countries)


@main_bp.route('/api/regions/<country_name>')
def api_regions(country_name):
    """Return regions/states/prefectures for a given country."""
    from global_countries import get_regions, get_region_label
    regions = get_regions(country_name)
    if not regions:
        return jsonify({"error": f"Country '{country_name}' not found"}), 404
    return jsonify({
        "country": country_name,
        "region_label": get_region_label(country_name),
        "regions": sorted(regions),
    })


@main_bp.route('/api/cities/<country_name>/<region_name>')
def api_cities(country_name, region_name):
    """Return cities for a given region within a country."""
    from global_countries import get_cities
    cities = get_cities(country_name, region_name)
    if not cities:
        return jsonify({"error": f"Region '{region_name}' not found in '{country_name}'"}), 404
    return jsonify({
        "country": country_name,
        "region": region_name,
        "cities": sorted(cities),
    })


@main_bp.route('/api/destinations/search')
def api_destination_search():
    """Search across all countries, regions, and cities."""
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    results = search_destinations(q)
    return jsonify(results[:20])


@main_bp.route('/api/trip-types')
def api_trip_types():
    """Return supported trip type options for the planner."""
    return jsonify({
        "trip_types": [
            {"id": "single_country", "label": "Single Country", "description": "Explore one country in depth"},
            {"id": "multi_country", "label": "Multi-Country", "description": "Travel across multiple countries with optimized routes"},
        ],
        "countries": ALL_COUNTRY_NAMES,
    })
