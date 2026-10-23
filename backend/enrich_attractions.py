import os
import random
import time
from datetime import date, datetime, timedelta
from io import BytesIO

import requests
from PIL import Image
from sqlalchemy import func

from app import create_app
from models import Attraction, Review, User, db


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    "User-Agent": "BelarusTourismStudentProject/1.0",
    "Referer": "https://commons.wikimedia.org/",
}
IMAGE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "static",
    "images",
    "attractions",
    "wikidata",
)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

IMAGE_FILES = {
    99: "File:Adam Mickiewicz house.jpg",
    102: "File:Catholic church of St. Andrew the Apostle and the Monastery of Trinitarian in Kryvičy - panoramio.jpg",
    132: "File:Church of Saints Boris and Gleb, Navahrudak 2018.jpg",
    134: "File:Kostel-1939-pinsk.jpg",
    139: "File:Гомель. Лялечны тэатр.jpg",
    142: "File:01034 Ivye 05 05.JPG",
    152: "File:Былая сядзіба Трамбіцкіх (Інтэрнацыянальны). Галоўны фасад.JPG",
}

REVIEW_TEXTS = [
    (
        "A memorable stop",
        "A beautiful and interesting place to visit. The surroundings were peaceful, and the site was easy to explore at a relaxed pace.",
    ),
    (
        "Worth visiting",
        "The architecture and local history made this a worthwhile stop. Allow enough time to walk around and notice the smaller details.",
    ),
    (
        "Good experience",
        "We enjoyed our visit and found the area clean and well maintained. It is a pleasant addition to a trip through this part of Belarus.",
    ),
    (
        "Interesting local landmark",
        "This landmark has plenty of character and gives a good sense of the region. Visiting earlier in the day made the experience quieter.",
    ),
    (
        "Pleasant visit",
        "The place was enjoyable and easy to reach. Information on site was limited, but the setting itself made the visit worthwhile.",
    ),
    (
        "Recommended for history lovers",
        "A rewarding place for anyone interested in Belarusian history and architecture. The atmosphere was calm and authentic.",
    ),
    (
        "A nice short visit",
        "We spent about an hour here and enjoyed the scenery. It works well as a short stop while exploring nearby towns.",
    ),
    (
        "Beautiful surroundings",
        "The location is photogenic and has a relaxed atmosphere. There were not many facilities, so it is useful to plan ahead.",
    ),
]


def download_commons_image(file_title, attraction_id):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    filename = f"{attraction_id}.jpg"
    path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return f"/static/images/attractions/wikidata/{filename}"

    response = requests.get(
        COMMONS_API,
        params={
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1200,
            "format": "json",
        },
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    info = (page.get("imageinfo") or [{}])[0]
    image_url = info.get("thumburl") or info.get("url")
    if not image_url:
        raise RuntimeError(f"No image URL returned for {file_title}")

    image = None
    for attempt in range(4):
        image = requests.get(image_url, headers=HEADERS, timeout=45)
        if image.status_code != 429:
            break
        time.sleep(3 * (attempt + 1))
    image.raise_for_status()
    if not image.headers.get("content-type", "").startswith("image/"):
        raise RuntimeError(f"Invalid image response for {file_title}")

    with open(path, "wb") as output:
        output.write(image.content)
    return f"/static/images/attractions/wikidata/{filename}"


def add_missing_images():
    updated = 0
    for attraction_id, file_title in IMAGE_FILES.items():
        attraction = db.session.get(Attraction, attraction_id)
        if not attraction or attraction.image_url:
            continue
        try:
            attraction.image_url = download_commons_image(file_title, attraction_id)
            db.session.commit()
            updated += 1
            print(f"Image: {attraction.name}")
            time.sleep(1)
        except requests.RequestException as error:
            db.session.rollback()
            print(f"Image skipped: {attraction.name} ({error})")
    return updated


def normalize_new_images():
    updated = 0
    attractions = Attraction.query.filter(Attraction.id >= 81)\
        .order_by(Attraction.id).all()

    for attraction in attractions:
        image_url = attraction.image_url or ""
        target_name = f"{attraction.id}.jpg"
        target_path = os.path.join(IMAGE_DIR, target_name)
        safe_url = f"/static/images/attractions/wikidata/{target_name}"

        try:
            if image_url == safe_url:
                with Image.open(target_path) as source:
                    source.verify()
                continue

            if image_url.startswith("/static/"):
                source_path = os.path.join(STATIC_DIR, image_url[len("/static/"):].replace("/", os.sep))
                with Image.open(source_path) as source:
                    image = source.convert("RGB")
                    image.thumbnail((1400, 1000), Image.Resampling.LANCZOS)
                    image.save(target_path, "JPEG", quality=88, optimize=True)
            elif image_url.startswith(("http://", "https://")):
                response = requests.get(image_url, headers=HEADERS, timeout=45)
                response.raise_for_status()
                with Image.open(BytesIO(response.content)) as source:
                    image = source.convert("RGB")
                    image.thumbnail((1400, 1000), Image.Resampling.LANCZOS)
                    image.save(target_path, "JPEG", quality=88, optimize=True)
            else:
                continue

            attraction.image_url = safe_url
            db.session.commit()
            updated += 1
            print(f"Normalized: {attraction.name}")
            time.sleep(0.2)
        except (OSError, requests.RequestException) as error:
            db.session.rollback()
            print(f"Normalize skipped: {attraction.name} ({error})")

    return updated


def add_demo_reviews():
    users = User.query.filter(User.username.like("seed_user%"))\
        .order_by(User.id).all()
    if not users:
        raise RuntimeError("Seed users are required before adding demo reviews")

    rng = random.Random(2742)
    attractions = Attraction.query.filter(Attraction.total_reviews == 0)\
        .order_by(Attraction.id).all()
    added = 0

    for attraction in attractions:
        existing = Review.query.filter_by(
            attraction_id=attraction.id,
            status="published",
        ).count()
        if existing:
            continue

        review_count = 5 + attraction.id % 4
        selected_users = rng.sample(users, review_count)
        ratings = []
        sentiments = []

        for index, user in enumerate(selected_users):
            title, content = REVIEW_TEXTS[(attraction.id + index) % len(REVIEW_TEXTS)]
            rating = rng.choice([3, 4, 4, 4, 5, 5, 5])
            sentiment = {3: 0.18, 4: 0.58, 5: 0.84}[rating]
            created_at = datetime.utcnow() - timedelta(days=rng.randint(8, 320))
            travel_date = date.today() - timedelta(days=rng.randint(20, 420))

            db.session.add(Review(
                user_id=user.id,
                attraction_id=attraction.id,
                title=title,
                content=content,
                rating=rating,
                travel_type=rng.choice(["solo", "couple", "family", "friends"]),
                travel_date=travel_date,
                travel_month=travel_date.strftime("%B"),
                helpful_count=rng.randint(0, 18),
                sentiment_label="positive" if rating >= 4 else "neutral",
                sentiment_score=sentiment,
                ai_processed=True,
                status="published",
                created_at=created_at,
                updated_at=created_at,
            ))
            ratings.append(rating)
            sentiments.append(sentiment)
            added += 1

        attraction.avg_rating = round(sum(ratings) / len(ratings), 2)
        attraction.total_reviews = len(ratings)
        attraction.sentiment_score = round(sum(sentiments) / len(sentiments), 3)
        attraction.sentiment_pos_count = sum(1 for rating in ratings if rating >= 4)
        attraction.sentiment_neg_count = sum(1 for rating in ratings if rating <= 2)

    db.session.commit()
    return added


def refresh_all_rating_totals():
    attractions = Attraction.query.all()
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
    app = create_app()
    with app.app_context():
        image_count = add_missing_images()
        normalized_count = normalize_new_images()
        review_count = add_demo_reviews()
        refresh_all_rating_totals()
        print(f"Done: {image_count} images, {normalized_count} normalized, {review_count} reviews")


if __name__ == "__main__":
    main()
