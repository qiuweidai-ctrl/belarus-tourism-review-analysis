from models import ReviewReply
from app import db
from .base_repository import BaseRepository


class ReplyRepository(BaseRepository):
    model = ReviewReply

    def get_by_review(self, review_id, page=1, per_page=20):
        return ReviewReply.query.filter_by(review_id=review_id).order_by(
            ReviewReply.created_at.asc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    def soft_delete(self, reply_id):
        from datetime import datetime
        reply = self.get_by_id(reply_id)
        if reply:
            reply.deleted_at = datetime.utcnow()
            db.session.commit()
        return reply
