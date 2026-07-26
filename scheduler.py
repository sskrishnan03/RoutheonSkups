import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)


def _run_daily_emails(app):
    with app.app_context():
        from models import db, User
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
                    _generate_smart_notifications(user, force=True)
                    sent = _send_pending_notification_emails(user)
                    total_sent += sent
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logger.exception("Daily email error for user_id=%s: %s", user.id, e)
            logger.info("Daily email job complete: %d emails sent to %d users.", total_sent, len(users))
        except Exception as e:
            logger.exception("Daily email job error: %s", e)


def start_scheduler(app):
    try:
        scheduler.add_job(
            _run_daily_emails,
            'interval',
            hours=24,
            id='daily_email_job',
            replace_existing=True,
            max_instances=1,
            args=[app],
        )
        scheduler.start()
        logger.warning("Scheduler started: daily email every 24 hours.")
    except Exception as e:
        logger.exception("Failed to start scheduler: %s", e)
