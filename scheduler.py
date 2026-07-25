import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)


def _run_notification_cycle():
    from app import create_app
    app = create_app()
    with app.app_context():
        from models import db, User, Notification
        from routes import (
            _get_notification_settings,
            _generate_smart_notifications,
            _send_pending_notification_emails,
        )
        try:
            users = User.query.all()
            total_sent = 0
            for user in users:
                try:
                    settings = _get_notification_settings(user)
                    if not settings.get('notifications_enabled', True):
                        continue
                    if not settings.get('email_notifications', True):
                        continue
                    _generate_smart_notifications(user)
                    sent = _send_pending_notification_emails(user)
                    total_sent += sent
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logger.exception("Notification cycle error for user_id=%s: %s", user.id, e)
            logger.info("Notification cycle complete: %d emails sent to %d users.", total_sent, len(users))
        except Exception as e:
            logger.exception("Global notification cycle error: %s", e)


def start_scheduler(interval_hours=3):
    try:
        scheduler.add_job(
            _run_notification_cycle,
            'interval',
            hours=interval_hours,
            id='notification_email_cycle',
            replace_existing=True,
            max_instances=1,
        )
        scheduler.start()
        logger.info("Notification scheduler started: every %d hours.", interval_hours)
    except Exception as e:
        logger.exception("Failed to start notification scheduler: %s", e)
