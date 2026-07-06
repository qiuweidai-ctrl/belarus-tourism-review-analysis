"""
Login Event Service —— 集中处理"登录事件"的写入。

为什么有这个：登录事件（login event）在俄语/英文语境里指的是
"一条记录：who/when/where/what" 而不是"登录这个动作本身"。
我们把所有 login-related 的动作（登录/注册/注销/失败/刷新/改密）都
统一通过这个服务写一条记录，方便审计和答辩演示。
"""
from datetime import datetime
from flask import request
from models import db, LoginEvent, LoginEventType


# 事件类型的展示名称（用于前端）
EVENT_LABELS = {
    'login':           'Login',
    'register':        'Register',
    'logout':          'Logout',
    'login_failed':    'Login Failed',
    'token_refresh':   'Token Refresh',
    'password_changed':'Password Changed',
}


def _client_ip():
    """获取客户端真实 IP（兼容反向代理）。"""
    return (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        or request.headers.get('X-Real-IP')
        or request.remote_addr
    )


def _user_agent():
    """截断 UA，避免超过字段长度。"""
    ua = request.headers.get('User-Agent', '')
    return ua[:500] if ua else None


def record_event(event_type, user=None, username=None, status='success', detail=None):
    """
    写入一条登录事件。

    用法：
        record_event('login', user=user)
        record_event('login_failed', username=attempted_username, status='failure',
                     detail='Invalid credentials')
    """
    try:
        # 防御一下：未知 event_type 仍然落库，但 detail 里说明
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
        # 事件日志失败不应阻塞主流程 —— 回滚并吞掉
        db.session.rollback()
        return None


def serialize_event(e: LoginEvent) -> dict:
    """给前端用的序列化。"""
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
