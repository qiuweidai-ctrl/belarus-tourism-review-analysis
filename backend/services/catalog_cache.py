from pathlib import Path
from threading import RLock
from time import monotonic

from flask import current_app, has_app_context
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from models import Attraction, ExternalRating


def init_catalog_cache(app):
    app.extensions['catalog_cache'] = {'lock': RLock(), 'values': {}, 'revision': None}


def revision_path():
    return Path(current_app.root_path).parent / '.runtime' / 'catalog.version'


# 目录统计缓存30秒，浏览量等实时数据不走这里。
def cached_catalog(key, load):
    state = current_app.extensions['catalog_cache']
    path = revision_path()
    revision = path.stat().st_mtime_ns if path.exists() else None
    with state['lock']:
        if state['revision'] != revision:
            state['values'].clear()
            state['revision'] = revision
        entry = state['values'].get(key)
        if entry and monotonic() < entry[0]:
            return entry[1]
        value = load()
        state['values'][key] = (monotonic() + 30, value)
        return value


@event.listens_for(Session, 'before_flush')
def catalog_changed(session, flush_context, instances):
    ignored = {'view_count', 'wishlist_count', 'avg_rating', 'total_reviews',
               'sentiment_score', 'sentiment_pos_count', 'sentiment_neg_count', 'updated_at'}
    for obj in session.new.union(session.deleted).union(session.dirty):
        if isinstance(obj, ExternalRating) or (
            isinstance(obj, Attraction) and (
                obj in session.new or obj in session.deleted or any(
                    inspect(obj).attrs[attribute.key].history.has_changes() and attribute.key not in ignored
                    for attribute in inspect(obj).mapper.column_attrs
                )
            )
        ):
            session.info['catalog_changed'] = True
            break


@event.listens_for(Session, 'after_commit')
def invalidate_catalog(session):
    if not session.info.pop('catalog_changed', False) or not has_app_context():
        return
    state = current_app.extensions.get('catalog_cache')
    if state:
        with state['lock']:
            state['values'].clear()
    from services.thumbnails import clear_thumbnail_cache
    clear_thumbnail_cache()
    if not current_app.testing:
        path = revision_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


@event.listens_for(Session, 'do_orm_execute')
def catalog_bulk_changed(state):
    if (state.is_update or state.is_delete) and state.bind_mapper is not None:
        if state.bind_mapper.class_ in (Attraction, ExternalRating):
            state.session.info['catalog_changed'] = True


@event.listens_for(Session, 'after_rollback')
def discard_catalog_changes(session):
    session.info.pop('catalog_changed', None)
