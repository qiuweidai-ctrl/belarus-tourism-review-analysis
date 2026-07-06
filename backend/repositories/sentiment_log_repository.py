from models import SentimentAnalysisLog
from app import db
from .base_repository import BaseRepository
import hashlib


class SentimentLogRepository(BaseRepository):
    model = SentimentAnalysisLog

    def find_by_review(self, review_id):
        return SentimentAnalysisLog.query.filter_by(review_id=review_id).first()

    def upsert(self, review_id, label, score, raw_response=None,
               model='deepseek-chat', processing_time_ms=None,
               status='success', confidence=None, fallback_method=None):
        existing = self.find_by_review(review_id)
        content_hash = hashlib.sha256(str(review_id).encode()).hexdigest()
        if existing:
            existing.sentiment_label = label
            existing.sentiment_score = score
            existing.raw_response = raw_response
            existing.status = status
            existing.confidence = confidence
            existing.model_used = model
            existing.processing_time_ms = processing_time_ms
            existing.fallback_method = fallback_method
            db.session.commit()
            return existing
        log = SentimentAnalysisLog(
            review_id=review_id,
            content_hash=content_hash,
            sentiment_label=label,
            sentiment_score=score,
            raw_response=raw_response,
            model_used=model,
            processing_time_ms=processing_time_ms,
            status=status,
            confidence=confidence,
            fallback_method=fallback_method
        )
        db.session.add(log)
        db.session.commit()
        return log
