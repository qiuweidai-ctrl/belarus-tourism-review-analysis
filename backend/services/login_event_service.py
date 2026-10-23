from datetime import datetime
from flask import request
from models import db, LoginEvent, LoginEventType


EVENT_LABELS = {
    'login':           'Login',
    'register':        'Register',
    'logout':          'Logout',
    'login_failed':    'Login Failed',
    'token_refresh':   'Token Refresh',
    'password_changed':'Password Changed',
}


def _client_ip():
    return (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        or request.headers.get('X-Real-IP')
        or request.remote_addr
    )


def _user_agent():
    ua = request.headers.get('User-Agent', '')
    return ua[:500] if ua else None


def record_event(event_type, user=None, username=None, status='success', detail=None):
    try:
        valid = {e.value for e in LoginEventType}
        if event_type not in valid:
            detail = (detail or '') + f' [unknown event_type: {event_type}]'

        evt = LoginEvent(
            user_id=user.id if user else None,
            username=username or (user.username if user else None),
            event_type=event_type,
            ip_address=_client_ip(),
            user_agent=_user_agent(),
            status=status,
            detail=detail,
            created_at=datetime.utcnow(),
        )
        db.session.add(evt)
        db.session.commit()
        return evt
    except Exception:
        db.session.rollback()
        return None


def serialize_event(e: LoginEvent) -> dict:
    return {
        'id': e.id,
        'user_id': e.user_id,
        'username': e.username,
        'event_type': e.event_type,
        'event_label': EVENT_LABELS.get(e.event_type, e.event_type),
        'ip_address': e.ip_address,
        'user_agent': e.user_agent,
        'status': e.status,
        'detail': e.detail,
        'created_at': e.created_at.isoformat() if e.created_at else None,
    }
