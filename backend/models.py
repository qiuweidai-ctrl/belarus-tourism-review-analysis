"""
SQLAlchemy ORM models for Belarus Tourism System.
All models use BIGINT/FLOAT/DECIMAL to match MySQL 8 schema.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, Enum as SQLEnum
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
    user = 'user'
    admin = 'admin'
    moderator = 'moderator'


class UserStatus(enum.Enum):
    active = 'active'
    banned = 'banned'
    inactive = 'inactive'


class ReviewStatus(enum.Enum):
    published = 'published'
    pending = 'pending'
    hidden = 'hidden'
    deleted = 'deleted'


class SentimentLabel(enum.Enum):
    positive = 'positive'
    neutral = 'neutral'
    negative = 'negative'


class AttractionCategory(enum.Enum):
    castle = 'castle'
    nature = 'nature'
    museum = 'museum'
    memorial = 'memorial'
    church = 'church'
    palace = 'palace'
    park = 'park'
    architecture = 'architecture'
    other = 'other'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    status = db.Column(db.String(20), nullable=False, default='active')
    bio = db.Column(db.Text, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')
    wishlists = db.relationship('Wishlist', backref='user', lazy='dynamic')


class Attraction(db.Model):
    __tablename__ = 'attractions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    name_be = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    short_desc = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    category = db.Column(db.String(30), nullable=False, default='other')
    suitable_season = db.Column(db.String(100), nullable=True)
    opening_hours = db.Column(db.String(200), nullable=True)
    ticket_price = db.Column(db.Numeric(10, 2), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    images_json = db.Column(db.JSON, nullable=True)
    avg_rating = db.Column(db.Numeric(3, 2), nullable=False, default=0.00)
    total_reviews = db.Column(db.Integer, nullable=False, default=0)
    sentiment_score = db.Column(db.Numeric(4, 3), nullable=True, default=0.000)
    sentiment_pos_count = db.Column(db.Integer, nullable=False, default=0)
    sentiment_neg_count = db.Column(db.Integer, nullable=False, default=0)
    wishlist_count = db.Column(db.Integer, nullable=False, default=0)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = db.relationship('Review', backref='attraction', lazy='dynamic')
    ratings = db.relationship('Rating', backref='attraction', lazy='dynamic')
    wishlists = db.relationship('Wishlist', backref='attraction', lazy='dynamic')

    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_region', 'region'),
        Index('idx_avg_rating', 'avg_rating'),
        Index('idx_is_featured', 'is_featured'),
    )


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)
    travel_type = db.Column(db.String(20), nullable=True)
    travel_date = db.Column(db.Date, nullable=True)
    travel_month = db.Column(db.String(20), nullable=True)
    helpful_count = db.Column(db.Integer, nullable=False, default=0)
    reply_count = db.Column(db.Integer, nullable=False, default=0)
    sentiment_label = db.Column(db.String(20), nullable=True)
    sentiment_score = db.Column(db.Numeric(4, 3), nullable=True, default=0.000)
    ai_processed = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='published')
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    replies = db.relationship('ReviewReply', backref='review', lazy='dynamic')
    sentiment_logs = db.relationship('SentimentAnalysisLog', backref='review', lazy='dynamic')
    helpful_votes = db.relationship('ReviewHelpfulVote', backref='review', lazy='dynamic')

    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_attraction_id', 'attraction_id'),
        Index('idx_rating', 'rating'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
    )


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'attraction_id', name='uk_user_attraction_rating'),
        Index('idx_ratings_attraction_id', 'attraction_id'),
    )


class ReviewReply(db.Model):
    __tablename__ = 'review_replies'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    review_id = db.Column(db.BigInteger, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        Index('idx_replies_review_id', 'review_id'),
        Index('idx_replies_user_id', 'user_id'),
    )


class Wishlist(db.Model):
    __tablename__ = 'wishlists'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False)
    note = db.Column(db.String(500), nullable=True)
    priority = db.Column(db.SmallInteger, nullable=False, default=3)
    visited = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'attraction_id', name='uk_user_attraction_wishlist'),
        Index('idx_wishlists_attraction_id', 'attraction_id'),
    )


class ReviewHelpfulVote(db.Model):
    __tablename__ = 'review_helpful_votes'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    review_id = db.Column(db.BigInteger, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_helpful = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('review_id', 'user_id', name='uk_review_user_vote'),
        Index('idx_votes_review_id', 'review_id'),
    )


class LoginToken(db.Model):
    __tablename__ = 'login_tokens'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(512), nullable=False)
    refresh_token = db.Column(db.String(512), nullable=True)
    device_info = db.Column(db.String(200), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    revoked_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        Index('idx_tokens_user_id', 'user_id'),
        Index('idx_tokens_expires_at', 'expires_at'),
    )


class SentimentAnalysisLog(db.Model):
    __tablename__ = 'sentiment_analysis_log'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    review_id = db.Column(db.BigInteger, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    content_hash = db.Column(db.String(64), nullable=True)
    raw_response = db.Column(db.JSON, nullable=True)
    sentiment_label = db.Column(db.String(20), nullable=False)
    sentiment_score = db.Column(db.Numeric(4, 3), nullable=False)
    confidence = db.Column(db.Numeric(5, 4), nullable=True)
    model_used = db.Column(db.String(100), nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    api_cost = db.Column(db.Numeric(8, 4), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='success')
    fallback_method = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('review_id', name='uk_sentiment_review_id'),
        Index('idx_sentiment_status', 'status'),
        Index('idx_sentiment_created_at', 'created_at'),
    )


# ============================================================
# 10. articles: 旅游攻略/文章表
# ============================================================
class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    summary = db.Column(db.String(600), nullable=True)
    content = db.Column(db.Text, nullable=False)
    cover_image_url = db.Column(db.String(500), nullable=True)
    tags_json = db.Column(db.JSON, nullable=True)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    comment_count = db.Column(db.Integer, nullable=False, default=0)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    is_published = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.String(20), nullable=False, default='published')
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    author = db.relationship('User', backref=db.backref('articles', lazy='dynamic'))
    attraction = db.relationship('Attraction', backref=db.backref('articles', lazy='dynamic'))
    article_likes = db.relationship('ArticleLike', backref='article', lazy='dynamic')
    article_comments = db.relationship('ArticleComment', backref='article', lazy='dynamic')

    __table_args__ = (
        Index('idx_articles_user_id', 'user_id'),
        Index('idx_articles_attraction_id', 'attraction_id'),
        Index('idx_articles_status', 'status'),
        Index('idx_articles_created_at', 'created_at'),
        Index('idx_articles_is_featured', 'is_featured'),
    )


class ArticleLike(db.Model):
    __tablename__ = 'article_likes'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    article_id = db.Column(db.BigInteger, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('article_id', 'user_id', name='uk_article_user_like'),
        Index('idx_likes_article_id', 'article_id'),
    )


class ArticleComment(db.Model):
    __tablename__ = 'article_comments'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    article_id = db.Column(db.BigInteger, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.BigInteger, nullable=True)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        Index('idx_comments_article_id', 'article_id'),
        Index('idx_comments_user_id', 'user_id'),
    )


# ============================================================
# 11. questions: 景点问答表
# ============================================================
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    answer_count = db.Column(db.Integer, nullable=False, default=0)
    upvote_count = db.Column(db.Integer, nullable=False, default=0)
    has_accepted_answer = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='published')
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    author = db.relationship('User', backref=db.backref('questions', lazy='dynamic'))
    attraction = db.relationship('Attraction', backref=db.backref('questions', lazy='dynamic'))
    answers = db.relationship('Answer', backref='question', lazy='dynamic')
    question_upvotes = db.relationship('QuestionUpvote', backref='question', lazy='dynamic')

    __table_args__ = (
        Index('idx_questions_user_id', 'user_id'),
        Index('idx_questions_attraction_id', 'attraction_id'),
        Index('idx_questions_status', 'status'),
        Index('idx_questions_created_at', 'created_at'),
    )


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    question_id = db.Column(db.BigInteger, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upvote_count = db.Column(db.Integer, nullable=False, default=0)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='published')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    author = db.relationship('User', backref=db.backref('answers', lazy='dynamic'))
    answer_upvotes = db.relationship('AnswerUpvote', backref='answer', lazy='dynamic')

    __table_args__ = (
        Index('idx_answers_question_id', 'question_id'),
        Index('idx_answers_user_id', 'user_id'),
        Index('idx_answers_is_accepted', 'is_accepted'),
    )


class QuestionUpvote(db.Model):
    __tablename__ = 'question_upvotes'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    question_id = db.Column(db.BigInteger, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('question_id', 'user_id', name='uk_question_user_upvote'),
        Index('idx_qup_question_id', 'question_id'),
    )


class AnswerUpvote(db.Model):
    __tablename__ = 'answer_upvotes'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    answer_id = db.Column(db.BigInteger, db.ForeignKey('answers.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('answer_id', 'user_id', name='uk_answer_user_upvote'),
        Index('idx_aup_answer_id', 'answer_id'),
    )


# ============================================================
# 12. tags: 景点标签表
# ============================================================
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(20), nullable=True)
    article_count = db.Column(db.Integer, nullable=False, default=0)
    use_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_tags_slug', 'slug'),
    )


class AttractionTag(db.Model):
    __tablename__ = 'attraction_tags'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.BigInteger, db.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('attraction_id', 'tag_id', name='uk_attraction_tag'),
        Index('idx_attag_attraction_id', 'attraction_id'),
        Index('idx_attag_tag_id', 'tag_id'),
    )


# ============================================================
# 13. rating_dimensions: 多维度评分表
# ============================================================
class RatingDimension(db.Model):
    __tablename__ = 'rating_dimensions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    attraction_id = db.Column(db.BigInteger, db.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False)
    scenery = db.Column(db.SmallInteger, nullable=True)
    service = db.Column(db.SmallInteger, nullable=True)
    value = db.Column(db.SmallInteger, nullable=True)
    facilities = db.Column(db.SmallInteger, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'attraction_id', name='uk_user_attraction_dimension'),
        Index('idx_dim_attraction_id', 'attraction_id'),
    )
