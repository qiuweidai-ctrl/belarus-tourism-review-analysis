import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app import create_app
from init_db import BELARUS_ATTRACTIONS, ensure_database_exists
from models import Attraction, AttractionTag, Review, Tag, User, db


DATA_FILE = Path(__file__).with_name("latest_attractions.json")

TAG_DEFINITIONS = {
    "history": ("History", "#8b4513"),
    "nature": ("Nature", "#2a9d5c"),
    "architecture": ("Architecture", "#1a5e63"),
    "memorial": ("Memorial", "#607d8b"),
    "museums": ("Museums", "#ff5722"),
    "religious": ("Religious Sites", "#673ab7"),
    "urban": ("Urban", "#9e9e9e"),
}

CATEGORY_TAGS = {
    "castle": ["history", "architecture"],
    "palace": ["history", "architecture"],
    "church": ["history", "religious"],
    "museum": ["history", "museums"],
    "memorial": ["history", "memorial"],
    "nature": ["nature"],
    "park": ["nature"],
    "architecture": ["architecture", "urban"],
}

REVIEW_TEXTS = [
    (
        "A memorable stop",
        "A beautiful and interesting place to visit. The surroundings were peaceful and the site was easy to explore.",
    ),
    (
        "Worth visiting",
        "The architecture and local history made this a worthwhile stop. Allow enough time to notice the smaller details.",
    ),
    (
        "Good experience",
        "We enjoyed the visit and found the area clean and well maintained. It was a pleasant part of our trip.",
    ),
    (
        "Interesting local landmark",
        "This landmark has plenty of character and gives a good sense of the region. Morning was especially quiet.",
    ),
    (
        "Beautiful surroundings",
        "The location is photogenic and has a relaxed atmosphere. It is useful to plan ahead for nearby facilities.",
    ),
]

PRESERVED_FIELDS = {
    "avg_rating",
    "total_reviews",
    "sentiment_score",
    "sentiment_pos_count",
    "sentiment_neg_count",
    "wishlist_count",
    "view_count",
}


def load_latest_attractions():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def ensure_default_users():
    defaults = [
        ("admin", "admin@belarus-tourism.com", "admin123", "admin", "Administrator"),
        ("demo", "demo@example.com", "demo123", "user", "Demo User"),
    ]
    for username, email, password, role, nickname in defaults:
        if User.query.filter(func.lower(User.username) == username).first():
            continue
        db.session.add(User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            nickname=nickname,
            status="active",
            email_verified=True,
        ))
    db.session.commit()


def ensure_seed_users():
    users = []
    for number in range(1, 9):
        username = f"portable_seed{number:02d}"
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                email=f"{username}@example.com",
                password_hash=generate_password_hash(f"seed-{number}-disabled"),
                nickname=f"Sample Visitor {number}",
                role="user",
                status="active",
                email_verified=True,
            )
            db.session.add(user)
    db.session.commit()
    for number in range(1, 9):
        users.append(User.query.filter_by(username=f"portable_seed{number:02d}").first())
    return users


def ensure_base_attractions():
    existing = {
        (item.name or "").strip().casefold(): item
        for item in Attraction.query.all()
    }
    added = 0
    for data in BELARUS_ATTRACTIONS:
        key = data["name"].strip().casefold()
        if key in existing:
            continue
        attraction = Attraction(**data)
        db.session.add(attraction)
        existing[key] = attraction
        added += 1
    db.session.commit()
    return added


def update_latest_attractions(records):
    existing = {
        (item.name or "").strip().casefold(): item
        for item in Attraction.query.all()
    }
    added = 0
    updated = 0
    for record in records:
        key = record["name"].strip().casefold()
        attraction = existing.get(key)
        values = {key: value for key, value in record.items() if key != "source_id"}
        if attraction is None:
            attraction = Attraction(**values)
            db.session.add(attraction)
            existing[key] = attraction
            added += 1
        else:
            for field, value in values.items():
                if field in PRESERVED_FIELDS:
                    continue
                setattr(attraction, field, value)
            updated += 1
    db.session.commit()
    return added, updated


def ensure_tags(attractions):
    tags = {}
    for slug, (name, color) in TAG_DEFINITIONS.items():
        tag = Tag.query.filter_by(slug=slug).first()
        if not tag:
            tag = Tag(name=name, slug=slug, color=color, description=name, use_count=0)
            db.session.add(tag)
        tags[slug] = tag
    db.session.commit()

    added = 0
    for attraction in attractions:
        for slug in CATEGORY_TAGS.get((attraction.category or "").lower(), []):
            tag = tags[slug]
            exists = AttractionTag.query.filter_by(
                attraction_id=attraction.id,
                tag_id=tag.id,
            ).first()
            if not exists:
                db.session.add(AttractionTag(attraction_id=attraction.id, tag_id=tag.id))
                added += 1
    db.session.commit()
    return added


def ensure_reviews(attractions, users):
    rng = random.Random(2742)
    created = 0
    base_time = datetime(2026, 10, 1, 12, 0, 0)
    for attraction in attractions:
        count = Review.query.filter_by(
            attraction_id=attraction.id,
            status="published",
        ).filter(Review.deleted_at.is_(None)).count()
        if count:
            continue
        ratings = []
        sentiments = []
        for index in range(5):
            title, content = REVIEW_TEXTS[index]
            rating = [4, 5, 4, 5, 3][(attraction.id + index) % 5]
            sentiment = {3: 0.18, 4: 0.58, 5: 0.84}[rating]
            visit_date = date(2026, 9, 1) - timedelta(days=(attraction.id + index) % 120)
            db.session.add(Review(
                user_id=users[(attraction.id + index) % len(users)].id,
                attraction_id=attraction.id,
                title=title,
                content=content,
                rating=rating,
                travel_type=["solo", "couple", "family", "friends"][index % 4],
                travel_date=visit_date,
                travel_month=visit_date.strftime("%B"),
                helpful_count=rng.randint(0, 12),
                sentiment_label="positive" if rating >= 4 else "neutral",
                sentiment_score=sentiment,
                ai_processed=True,
                status="published",
                created_at=base_time - timedelta(days=(attraction.id + index) % 90),
                updated_at=base_time - timedelta(days=(attraction.id + index) % 90),
            ))
            ratings.append(rating)
            sentiments.append(sentiment)
            created += 1
        attraction.avg_rating = round(sum(ratings) / len(ratings), 2)
        attraction.total_reviews = len(ratings)
        attraction.sentiment_score = round(sum(sentiments) / len(sentiments), 3)
        attraction.sentiment_pos_count = sum(1 for value in ratings if value >= 4)
        attraction.sentiment_neg_count = sum(1 for value in ratings if value <= 2)
    db.session.commit()
    return created


def refresh_rating_totals(attractions):
    for attraction in attractions:
        stats = db.session.query(
            func.avg(Review.rating),
            func.count(Review.id),
        ).filter(
            Review.attraction_id == attraction.id,
            Review.status == "published",
            Review.deleted_at.is_(None),
        ).first()
        if stats and stats[1]:
            attraction.avg_rating = round(float(stats[0]), 2)
            attraction.total_reviews = int(stats[1])
    db.session.commit()


def main():
    print("Checking database...")
    ensure_database_exists()
    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_default_users()
        base_added = ensure_base_attractions()
        records = load_latest_attractions()
        latest_added, latest_updated = update_latest_attractions(records)
        attractions = Attraction.query.order_by(Attraction.id).all()
        seed_users = ensure_seed_users()
        tag_count = ensure_tags(attractions)
        review_count = ensure_reviews(attractions, seed_users)
        refresh_rating_totals(attractions)
        print(
            "Database ready: "
            f"{base_added} base attractions added, "
            f"{latest_added} latest attractions added, "
            f"{latest_updated} latest attractions updated, "
            f"{tag_count} tags linked, "
            f"{review_count} sample reviews added."
        )


if __name__ == "__main__":
    main()
