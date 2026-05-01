from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from models import db, User, Trip, Destination, Itinerary, SavedDestination, Notification
from services import AIService, WeatherService
# from graph_service import graph_service
import json
from datetime import datetime, timedelta, timezone
import random
from flask_login import login_user, current_user, logout_user, login_required
from app import bcrypt, mail
from flask_mail import Message
import os
import mimetypes
import html
import base64
from uuid import uuid4
from werkzeug.utils import secure_filename

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

INDIA_PROMPT_DESTINATIONS = [
    "Goa", "Jaipur", "Udaipur", "Jaisalmer", "Rishikesh", "Manali", "Shimla", "Dharamshala",
    "Leh", "Srinagar", "Amritsar", "Varanasi", "Agra", "Delhi", "Mumbai", "Pune", "Bengaluru",
    "Mysuru", "Coorg", "Ooty", "Kodaikanal", "Chennai", "Pondicherry", "Hyderabad", "Hampi",
    "Kochi", "Munnar", "Alleppey", "Thekkady", "Madurai", "Kolkata", "Darjeeling", "Gangtok",
    "Shillong", "Kaziranga", "Guwahati", "Bhubaneswar", "Puri", "Konark", "Andaman", "Lakshadweep",
    "Auli", "Nainital", "Mussoorie", "Khajuraho"
]


def _get_daily_ai_inspiration_prompts():
    """Return 15 India trip prompt inspirations that rotate daily (IST)."""
    ist_today = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    rng = random.Random(f"daily-ai-prompts-{ist_today.isoformat()}")

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

    destinations = INDIA_PROMPT_DESTINATIONS[:]
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


def _send_notification_email(user, subject, message, created_at=None):
    if not user.email:
        return
    sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
    if not sender:
        return
    sent_at = created_at.strftime('%d %b %Y, %I:%M %p UTC') if created_at else datetime.utcnow().strftime('%d %b %Y, %I:%M %p UTC')
    msg = Message(subject=subject, recipients=[user.email])
    msg.body = (
        f"Hello {user.name},\n\n"
        "You have a new notification from RoutheonSkups.\n\n"
        f"Time: {sent_at}\n"
        f"Message: {message}\n\n"
        "Open RoutheonSkups to view details.\n\n"
        "RoutheonSkups Team"
    )
    mail.send(msg)


def _generate_smart_notifications(user, force=False):
    settings = _get_notification_settings(user)
    if not settings.get('notifications_enabled', True):
        return 0
    ai_settings = _get_ai_assistant_settings(user)
    now = datetime.utcnow()
    today = now.date()
    prefs = _get_user_preferences(user)
    meta = prefs.get('notification_meta', {}) if isinstance(prefs.get('notification_meta', {}), dict) else {}
    created = []
    meta_changed = False
    global_cooldown_hours = 3

    # Global notification pacing: don't disturb users too often.
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

        notif = Notification(user_id=user.id, message=message, type=notif_type)
        db.session.add(notif)
        created.append((notif, email_subject or "RoutheonSkups Notification"))
        meta[meta_key] = now.isoformat()
        meta_changed = True

    # Trip alerts for upcoming trips.
    upcoming_trips = Trip.query.filter(
        Trip.user_id == user.id,
        Trip.start_date >= today
    ).order_by(Trip.start_date.asc()).limit(20).all()

    for trip in upcoming_trips:
        days_left = (trip.start_date - today).days
        if days_left in (0, 1, 3, 7):
            if days_left == 0:
                msg = f"Trip Alert: Your trip to {trip.destination} starts today. Have a great journey!"
            elif days_left == 1:
                msg = f"Trip Alert: Your trip to {trip.destination} starts tomorrow. Pack your essentials."
            else:
                msg = f"Trip Alert: {trip.destination} starts in {days_left} days. Time to finalize plans."
            maybe_add(
                'trip_alerts',
                f"trip_alert:{trip.id}:{days_left}",
                18,
                msg,
                notif_type='trip',
                email_subject=f"Trip Alert: {trip.destination}"
            )

    # Season-wise suggestions from saved and recent destinations.
    month = now.month
    season_map = {
        1: "Winter", 2: "Winter", 3: "Summer", 4: "Summer", 5: "Summer",
        6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
        10: "Post-Monsoon", 11: "Winter", 12: "Winter"
    }
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
            maybe_add(
                'ai_suggestions',
                f"ai_suggestion:{month}:{focus}",
                72,
                f"AI Suggestion: Since you saved {focus}, this {season} is great to revisit {top_three}.",
                notif_type='info',
                email_subject="AI Suggestion for Your Next Trip"
            )
        maybe_add(
            'seasonal_recommendations',
            f"seasonal:{month}",
            168,
            f"Seasonal Recommendation: {season} travel picks from your interests - {top_three}.",
            notif_type='info',
            email_subject=f"{season} Travel Recommendation"
        )

    # System notifications (monthly).
    month_key = now.strftime('%Y-%m')
    maybe_add(
        'system_notifications',
        f"system:{month_key}",
        720,
        "System Notification: Platform reliability checks completed. Your account and trip data are healthy.",
        notif_type='warning',
        email_subject="System Notification"
    )

    if meta_changed:
        _set_notification_meta(user, meta)

    if created:
        meta['last_notification_sent_at'] = now.isoformat()
        _set_notification_meta(user, meta)
        db.session.commit()
        if settings.get('email_notifications', True):
            for notif, subject in created:
                try:
                    _send_notification_email(user, subject, notif.message, notif.created_at)
                except Exception as e:
                    print(f"Notification email send error: {e}")
    elif meta_changed:
        db.session.commit()

    return len(created)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    return render_template('firstpage.html')

@main_bp.route('/secondpage')
def secondpage():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    return render_template('secondpage.html')

@main_bp.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    return render_template('landing page.html')

@main_bp.route('/landing')
@login_required
def landing():
    return render_template('landing_page.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.landing'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                token = user.get_reset_token()
                msg = Message('Password Reset Request',
                            recipients=[email])
                msg.body = f'''To reset your password, visit the following link:
{url_for('main.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
                mail.send(msg)
                flash('An email has been sent with instructions to reset your password.', 'success')
            except Exception as e:
                print(f"Error sending email: {e}")
                flash('There was an error sending the reset email. Please try again later.', 'danger')
        else:
            # For security reasons, we still show the success message even if the user doesn't exist
            flash('If an account exists with that email, a password reset link has been sent.', 'success')
            
        return redirect(url_for('main.login'))
    return redirect(url_for('main.login'))

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
    redirect_uri = "https://routheonskups.onrender.com/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri, prompt='select_account')

@main_bp.route('/auth/google/callback')
def google_callback():
    oauth = current_app.extensions['authlib.integrations.flask_client']
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        flash('Google authentication failed.', 'danger')
        return redirect(url_for('main.login'))

    google_id = user_info['sub']
    email = user_info['email']
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

    login_user(user)
    return redirect(url_for('main.landing'))

@main_bp.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.landing'))
    from models import User
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.landing'))
    
    from models import User, Trip, Destination, SavedDestination
    
    # Platform Metrics
    total_users = User.query.count()
    total_trips = Trip.query.count()
    total_destinations = Destination.query.count()
    total_saves = SavedDestination.query.count()
    
    # Recent Activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                          total_users=total_users,
                          total_trips=total_trips,
                          total_destinations=total_destinations,
                          total_saves=total_saves,
                          recent_users=recent_users)

@main_bp.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    if current_user.id == user_id:
        return jsonify({'success': False, 'message': 'You cannot delete your own account'}), 400
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

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
    
    # Optionally save this to the DB if we want it to persist immediately
    # For now, let's just return it for the UI to display
    return jsonify(plan)

@main_bp.route('/explore')
@login_required
def explore():
    return render_template('explore.html')

@main_bp.route('/my-trips')
@login_required
def my_trips():
    today = datetime.now().date()
    all_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).all()
    show_saved_all = (request.args.get('saved') or '').lower() == 'all'
    show_explored_all = (request.args.get('explored') or '').lower() == 'all'
    
    upcoming_trips = [t for t in all_trips if t.start_date > today]
    past_trips = [t for t in all_trips if t.end_date < today]
    # "Created Journeys" can be used for all trips or ones that aren't strictly history/upcoming
    
    trip_count = len(current_user.trips)
    saved_count = len(current_user.saved_destinations)
    
    all_saved = SavedDestination.query.filter_by(user_id=current_user.id).order_by(SavedDestination.created_at.desc()).all()
    recent_saved = all_saved[:2]

    explored_trips_raw = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.created_at.desc()).all()
    recent_trips_raw = explored_trips_raw[:2]
    
    recent_trips = []
    for t in recent_trips_raw:
        img_url = "https://images.unsplash.com/photo-1548013146-72479768bbaa?auto=format&fit=crop&q=80&w=2000"
        try:
            if t.itinerary_text:
                plan = json.loads(t.itinerary_text)
                if plan.get('hero_image'):
                    img_url = plan['hero_image']
        except:
            pass
        t.display_image = img_url
        recent_trips.append(t)

    explored_trips = []
    for t in explored_trips_raw:
        img_url = "https://images.unsplash.com/photo-1548013146-72479768bbaa?auto=format&fit=crop&q=80&w=2000"
        try:
            if t.itinerary_text:
                plan = json.loads(t.itinerary_text)
                if plan.get('hero_image'):
                    img_url = plan['hero_image']
        except:
            pass
        t.display_image = img_url
        explored_trips.append(t)
    
    return render_template('profile_page2.html', 
                           upcoming_trips=upcoming_trips, 
                           past_trips=past_trips, 
                           all_trips=all_trips,
                           trip_count=trip_count,
                           saved_count=saved_count,
                           recent_saved=recent_saved,
                           recent_trips=recent_trips,
                           all_saved=all_saved,
                           explored_trips=explored_trips,
                           show_saved_all=show_saved_all,
                           show_explored_all=show_explored_all)

@main_bp.route('/destination/<name>')
@login_required
def destination_info(name):
    data = AIService.get_destination_detail(name)
    lat = data.get('center_coords', {}).get('lat')
    lon = data.get('center_coords', {}).get('lng')
    weather = WeatherService.get_forecast(name, lat=lat, lon=lon)
    return render_template('destination.html', name=name, data=data, weather=weather)

@main_bp.route('/create-trip')
@login_required
def create_trip():
    india_destinations = [
        "Goa", "Jaipur", "Udaipur", "Jaisalmer", "Rishikesh", "Manali", "Shimla", "Dharamshala",
        "Leh", "Srinagar", "Amritsar", "Varanasi", "Agra", "Delhi", "Mumbai", "Pune", "Bengaluru",
        "Mysuru", "Coorg", "Ooty", "Kodaikanal", "Chennai", "Pondicherry", "Hyderabad", "Hampi",
        "Kochi", "Munnar", "Alleppey", "Thekkady", "Madurai", "Kolkata", "Darjeeling", "Gangtok",
        "Shillong", "Kaziranga", "Guwahati", "Bhubaneswar", "Puri", "Konark", "Andaman", "Lakshadweep",
        "Auli", "Nainital", "Mussoorie", "Khajuraho"
    ]

    # Rotate by IST date so the list changes once per day and stays stable throughout that day.
    ist_today = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    day_number = ist_today.toordinal()
    start_index = (day_number * 7) % len(india_destinations)
    daily_destinations = [
        india_destinations[(start_index + i) % len(india_destinations)]
        for i in range(20)
    ]
    random.Random(f"india-popular-{ist_today.isoformat()}").shuffle(daily_destinations)

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
    try:
        parsed = json.loads(trip.itinerary_text) if trip.itinerary_text else []
        if isinstance(parsed, dict):
            itinerary = parsed.get('itinerary', []) or []
            weather = parsed.get('weather', {}) or {}
            chat = parsed.get('chat', []) or []
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
        chat=chat
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

@main_bp.route('/profile')
@login_required
def profile():
    trip_count = len(current_user.trips)
    saved_count = len(current_user.saved_destinations)
    saved_destinations = current_user.saved_destinations
    user_prefs = _get_user_preferences(current_user).get('categories', [])
    return render_template('profile_page1.html', 
                           trip_count=trip_count, 
                           saved_count=saved_count,
                           saved_destinations=saved_destinations,
                           user_prefs=user_prefs)

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
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))


@main_bp.route('/profile/image/upload', methods=['POST'])
@login_required
def upload_profile_image():
    file = request.files.get('profile_image')
    if not file or not file.filename:
        flash('Please select an image file to upload.', 'error')
        return redirect(request.referrer or url_for('main.profile'))

    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    content_type = (file.mimetype or '').lower()
    if extension not in ALLOWED_PROFILE_IMAGE_EXTENSIONS and not content_type.startswith('image/'):
        flash('Unsupported file type. Please upload an image.', 'error')
        return redirect(request.referrer or url_for('main.profile'))

    upload_dir = os.path.join(current_app.static_folder, PROFILE_UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    unique_name = f"user_{current_user.id}_{uuid4().hex}.{extension or 'jpg'}"
    save_path = os.path.join(upload_dir, unique_name)
    file.save(save_path)

    old_image_url = current_user.image_url
    current_user.image_url = url_for('static', filename=f"{PROFILE_UPLOAD_DIR.replace(os.sep, '/')}/{unique_name}")
    db.session.commit()
    _delete_local_profile_image(old_image_url)

    flash('Profile image updated successfully.', 'success')
    return redirect(request.referrer or url_for('main.profile'))


@main_bp.route('/profile/image/delete', methods=['POST'])
@login_required
def delete_profile_image():
    old_image_url = current_user.image_url
    if old_image_url:
        current_user.image_url = None
        db.session.commit()
        _delete_local_profile_image(old_image_url)
        flash('Profile image deleted.', 'success')
    else:
        flash('No profile image found.', 'info')
    return redirect(request.referrer or url_for('main.profile'))

@main_bp.route('/calendar')
@login_required
def calendar():
    today = datetime.now().date()
    all_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).all()
    upcoming_trips = [t for t in all_trips if t.start_date >= today]
    past_trips = [t for t in all_trips if t.end_date < today]
    
    trip_count = len(current_user.trips)
    saved_count = len(current_user.saved_destinations)
    
    # Prepare trips for JS (JSON serializable)
    trips_data = []
    for t in all_trips:
        trips_data.append({
            'id': t.id,
            'destination': t.destination,
            'start_date': t.start_date.isoformat(),
            'end_date': t.end_date.isoformat(),
            'budget': t.budget
        })

    return render_template('profile_page3.html', 
                           upcoming_trips=upcoming_trips,
                           past_trips=past_trips,
                           all_trips_js=trips_data,
                           trip_count=trip_count,
                           saved_count=saved_count)

@main_bp.route('/settings')
@login_required
def settings():
    trip_count = len(current_user.trips)
    saved_count = len(current_user.saved_destinations)
    notification_settings = _get_notification_settings(current_user)
    ai_assistant_settings = _get_ai_assistant_settings(current_user)
    return render_template('profile_page4.html', 
                           trip_count=trip_count, 
                           saved_count=saved_count,
                           notification_settings=notification_settings,
                           ai_assistant_settings=ai_assistant_settings)


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
    flash('Notification settings updated successfully.', 'success')
    return redirect(url_for('main.settings'))


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

    return redirect(url_for('main.settings'))

@main_bp.route('/profile-ai')
@login_required
def profile_ai():
    trip_count = len(current_user.trips)
    saved_count = len(current_user.saved_destinations)
    ai_assistant_settings = _get_ai_assistant_settings(current_user)
    return render_template('profile_page5.html', 
                           trip_count=trip_count, 
                           saved_count=saved_count,
                           ai_assistant_settings=ai_assistant_settings)

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
    
    data = AIService.explore_destinations(
        state=state if state else None,
        category=category if category else None,
        search_query=search_query if search_query else None,
        page=page
    )
    return jsonify(data)

@main_bp.route('/api/destination-attractions')
@login_required
def api_destination_attractions():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_attractions(name)
    return jsonify(data)

@main_bp.route('/api/destination-itinerary')
@login_required
def api_destination_itinerary():
    name = request.args.get('name', '')
    days = request.args.get('days', 3, type=int)
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_itinerary(name, days=days)
    return jsonify(data)

@main_bp.route('/api/destination-gallery')
@login_required
def api_destination_gallery():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Destination name required"}), 400
    data = AIService.get_gallery(name)
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
    return jsonify({"success": True, "saved": True})

@main_bp.route('/api/check-saved')
@login_required
def check_saved():
    name = request.args.get('name')
    if not name:
        return jsonify({"saved": False})
    saved = SavedDestination.query.filter_by(user_id=current_user.id, name=name).first()
    return jsonify({"saved": bool(saved)})

@main_bp.route('/api/get-destination-story')
@login_required
def get_destination_story():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name required"}), 400
    story_data = AIService.generate_destination_story(name)
    return jsonify(story_data)

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

        # Use a natural-sounding neural voice (India English by default)
        voice = request.args.get('voice', 'en-IN-NeerjaNeural')
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
            tts = gTTS(text=text[:5000], lang='en', tld='co.in', slow=False)
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
        return jsonify({"error": "Weather unavailable"}), 404
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
        
        system_prompt = f"""You are Skupheon AI, an expert travel guide for {destination}, India. 
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
    return jsonify({"reply": response})

@main_bp.route('/api/save-itinerary', methods=['POST'])
@login_required
def save_itinerary():
    try:
        data = request.json
        destination = data.get('destination', 'Magic Trip')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        budget = data.get('budget', 'Medium')
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

        saved_payload = {
            "schema_version": 2,
            "destination": destination,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "budget": budget,
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
        
        # Add notification
        notif = None
        notif_settings = _get_notification_settings(current_user)
        if notif_settings.get('notifications_enabled', True) and notif_settings.get('trip_alerts', True):
            notif = Notification(
                user_id=current_user.id,
                message=f"Success! Your trip to {destination} has been saved.",
                type='success'
            )
            db.session.add(notif)
        
        db.session.commit()
        try:
            if notif and _get_notification_settings(current_user).get('email_notifications', True):
                _send_notification_email(
                    current_user,
                    f"Trip Saved: {destination}",
                    notif.message,
                    notif.created_at
                )
        except Exception as e:
            print(f"Trip notification email error: {e}")
        return jsonify({"success": True, "trip_id": trip.id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

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
    
    if not message_text and not image_base64:
        return jsonify({"error": "Message or image required"}), 400
    
    if not chat_history_enabled:
        if image_base64:
            try:
                image_bytes = base64.b64decode(image_base64)
            except Exception:
                return jsonify({"error": "Invalid image payload"}), 400
            ai_response_text = AIService.analyze_image_for_travel(image_bytes, image_mime, message_text)
        else:
            ai_response_text = AIService.general_chat(message_text, history=[])
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
    # We take the last 5-10 messages for context
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
        ai_response_text = AIService.general_chat(message_text, history=history[:-1]) # history[:-1] because history already includes user_msg
    
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
                from zoneinfo import ZoneInfo
                submitted_dt = datetime.now(ZoneInfo("Asia/Kolkata"))
                submitted_on = submitted_dt.strftime("%d %b %Y, %I:%M %p %Z")
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
            <div style="font-family:Arial,sans-serif;background:#f8fafc;padding:24px;">
              <div style="max-width:700px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;overflow:hidden;">
                <div style="background:#2563eb;color:#ffffff;padding:20px 24px;">
                  <div style="display:flex;align-items:center;gap:12px;">{logo_html}</div>
                  <h1 style="margin:12px 0 0;font-size:20px;line-height:1.3;">New Contact Form Submission</h1>
                  <p style="margin:8px 0 0;font-size:13px;opacity:0.95;">Project: RoutheonSkups | Submitted on {submitted_on}</p>
                </div>
                <div style="padding:24px;">
                  <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:8px 0;color:#475569;width:180px;"><strong>Name</strong></td><td style="padding:8px 0;color:#0f172a;">{esc_name}</td></tr>
                    <tr><td style="padding:8px 0;color:#475569;"><strong>Email</strong></td><td style="padding:8px 0;color:#0f172a;">{esc_email}</td></tr>
                    <tr><td style="padding:8px 0;color:#475569;"><strong>Phone</strong></td><td style="padding:8px 0;color:#0f172a;">{esc_phone}</td></tr>
                    <tr><td style="padding:8px 0;color:#475569;"><strong>Subject</strong></td><td style="padding:8px 0;color:#0f172a;">{esc_subject}</td></tr>
                    <tr><td style="padding:8px 0;color:#475569;"><strong>Trip Reference</strong></td><td style="padding:8px 0;color:#0f172a;">{esc_trip_ref}</td></tr>
                  </table>
                  <div style="margin-top:18px;">
                    <p style="margin:0 0 8px;color:#475569;"><strong>Message</strong></p>
                    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;color:#0f172a;white-space:pre-wrap;">{esc_message}</div>
                  </div>
                </div>
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
            <div style="font-family:Arial,sans-serif;background:#f8fafc;padding:24px;">
                <div style="max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;overflow:hidden;">
                <div style="background:#2563eb;color:#ffffff;padding:20px 24px;">
                  <div style="display:flex;align-items:center;gap:12px;">{user_logo_html}</div>
                  <p style="margin:8px 0 0;font-size:14px;opacity:0.95;">We received your message</p>
                </div>
                <div style="padding:24px;">
                  <p style="margin:0 0 12px;color:#0f172a;">Hi {esc_name},</p>
                  <p style="margin:0 0 12px;color:#334155;">Thank you for contacting RoutheonSkups. Our team has received your request and will get back to you soon.</p>
                  <p style="margin:0 0 4px;color:#475569;"><strong>Submitted On:</strong> {submitted_on}</p>
                  <p style="margin:0 0 16px;color:#475569;"><strong>Subject:</strong> {esc_subject}</p>
                  <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;color:#0f172a;white-space:pre-wrap;">{esc_message}</div>
                  <p style="margin:16px 0 0;color:#64748b;font-size:13px;">This is an automated acknowledgment from the RoutheonSkups Contact Center.</p>
                </div>
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

