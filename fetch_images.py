"""
Fetch real images for all Belarus attractions and store them locally.

Strategy (no API key required):
  1. Re-download existing Wikipedia URLs with a proper User-Agent.
     If a URL fails, mark the attraction for replacement.
  2. For attractions still missing an image, query loremflickr.com by
     category-specific keywords. loremflickr returns real Flickr photos
     matching the tags. Domestic China-friendly.
  3. Final fallback: picsum.photos with a stable per-attraction seed
     (still real photos, just not topic-specific).
  4. Update attractions.image_url to /static/images/attractions/{id}.jpg.

Run:  python fetch_images.py
"""
import os
import re
import time
import requests
import pymysql

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "backend", "static", "images", "attractions")
os.makedirs(IMG_DIR, exist_ok=True)

W, H = 800, 600

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Per-category fallback tags (used in order with overrides) ──
CATEGORY_TAGS = {
    "castle":       ["castle", "medieval"],
    "palace":       ["palace", "baroque"],
    "church":       ["church", "cathedral"],
    "museum":       ["museum", "exhibition"],
    "memorial":     ["memorial", "monument"],
    "nature":       ["forest", "lake"],
    "park":         ["park", "nature"],
    "architecture": ["architecture", "european"],
    "other":        ["city", "building"],
}

# ── Attraction-specific overrides (substring of lower(name) -> tags) ──
# More specific terms get appended first.
SPECIFIC_OVERRIDES = [
    ("mir castle",           ["mir castle belarus"]),
    ("nesvizh",              ["nesvizh palace"]),
    ("belovezhskaya",        ["bison forest"]),
    ("lida",                 ["lida castle"]),
    ("brest fortress",       ["brest fortress"]),
    ("khatyn",               ["khatyn memorial"]),
    ("kurapaty",             ["forest cross memorial"]),
    ("great patriotic war",  ["war museum"]),
    ("national art museum",  ["art museum painting"]),
    ("chagall",              ["chagall painting"]),
    ("st sophia",            ["orthodox cathedral baroque"]),
    ("red church",           ["red church gothic"]),
    ("holy trinity",         ["gothic church twin tower"]),
    ("borys and gleb",       ["ancient church ruins"]),
    ("ss. boris",            ["ancient church ruins"]),
    ("gomel palace",         ["palace riverside"]),
    ("kosava",               ["baroque palace"]),
    ("kossovsky",            ["baroque palace"]),
    ("minsk",                ["minsk city"]),
    ("victory square",       ["victory square"]),
    ("eternal flame",        ["eternal flame"]),
    ("plamya",               ["monument obelisk"]),
    ("island of tears",      ["war memorial sculpture"]),
    ("st nicholas",          ["orthodox monastery"]),
    ("zhyrovichy",           ["monastery pilgrimage"]),
    ("borisoglebskaya",      ["wooden church"]),
    ("mogilev",              ["historic city"]),
    ("vitebsk",              ["vitebsk"]),
    ("polotsk",              ["polotsk"]),
    ("grodno",               ["grodno"]),
    ("brest",                ["brest city"]),
    ("narach",               ["lake narach"]),
    ("naroch",               ["lake narach"]),
    ("pripyatsky",           ["wetland nature"]),
    ("berezina",             ["river nature"]),
    ("augustow canal",       ["canal nature"]),
    ("blue lakes",           ["blue lakes"]),
    ("strait of riga",       ["seashore"]),
    ("navahrudak",           ["castle ruins"]),
    ("krevo",                ["castle ruins"]),
    ("lubcha",               ["castle ruins"]),
    ("kamyanets",            ["stone tower"]),
    ("kamieniec",            ["stone tower"]),
    ("berestye",             ["archaeology wood"]),
    ("belaya vezha",         ["stone tower"]),
]


def get_tags(name: str, category: str) -> str:
    """Return a single short normalized tag for loremflickr.

    loremflickr rejects spaces and ~>12-char first-segment tags, so we
    pick ONE short single-word tag (preferring category, plus an
    attraction-specific override if it fits).
    """
    nl = name.lower()
    cat_tags = CATEGORY_TAGS.get(category or "other", CATEGORY_TAGS["other"])
    specific = None
    for key, extra in SPECIFIC_OVERRIDES:
        if key in nl:
            specific = extra
            break
    # Pick the shortest single-word tag from specific or category
    raw = (specific[0] if specific else cat_tags[0]).split()[0]
    tag = re.sub(r"[^a-z0-9]+", "", raw.lower())
    if not tag:
        tag = "european"
    # Cap to ~10 chars to avoid loremflickr 404s
    return tag[:10] or "european"


def loremflickr_url(tag: str, lock_id: int) -> str:
    """loremflickr single-tag URL with lock for stability."""
    return f"https://loremflickr.com/{W}/{H}/{tag}?lock={lock_id}"


def is_image_response(resp: requests.Response) -> bool:
    ct = resp.headers.get("Content-Type", "").lower()
    return resp.status_code == 200 and ct.startswith("image/") and len(resp.content) > 1024


def fetch(url: str, timeout: int = 15) -> bytes | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r.content if is_image_response(r) else None
    except Exception:
        return None


def wikipedia_url_for(attraction_id: int, name: str) -> str | None:
    """Build a Wikipedia URL for the attraction (English Wikipedia, summary endpoint)."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"https://en.wikipedia.org/wiki/{slug}"


def main():
    print(f"Image directory: {IMG_DIR}")
    conn = pymysql.connect(host="localhost", user="root", password="123456",
                          database="belarus_tourism", charset="utf8mb4")
    cur = conn.cursor()
    cur.execute("SELECT id, name, category, image_url FROM attractions ORDER BY id")
    rows = cur.fetchall()
    print(f"Total attractions: {len(rows)}\n")

    success, failed = [], []
    for aid, name, category, image_url in rows:
        out_path = os.path.join(IMG_DIR, f"{aid}.jpg")
        local_rel = f"/static/images/attractions/{aid}.jpg"

        # Skip if already a valid local file
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
            if image_url != local_rel:
                cur.execute("UPDATE attractions SET image_url=%s WHERE id=%s",
                            (local_rel, aid))
                conn.commit()
            print(f"  [{aid:3d}] {name[:48]:48s} (cached)")
            success.append(aid)
            continue

        data, source = None, None

        # 1) Existing Wikipedia URL with proper UA
        if image_url and "wikipedia" in image_url.lower():
            data = fetch(image_url)
            if data:
                source = "wikipedia"

        # 2) Wikipedia commons direct (search by slug)
        if data is None:
            wp = wikipedia_url_for(aid, name)
            if wp:
                data = fetch(wp)
                if data:
                    source = "wikipedia-summary"

        # 3) loremflickr with curated tag
        if data is None:
            tag = get_tags(name, category)
            url = loremflickr_url(tag, aid)
            data = fetch(url)
            if data:
                source = f"loremflickr({tag})"

        # 4) picsum fallback (real photo, not topic-specific)
        if data is None:
            url = f"https://picsum.photos/seed/{aid}/{W}/{H}"
            data = fetch(url)
            if data:
                source = "picsum"

        if data:
            with open(out_path, "wb") as f:
                f.write(data)
            cur.execute("UPDATE attractions SET image_url=%s WHERE id=%s",
                        (local_rel, aid))
            conn.commit()
            print(f"  [{aid:3d}] {name[:48]:48s} {len(data)//1024:5d}KB  {source}")
            success.append(aid)
        else:
            failed.append((aid, name))
            print(f"  [{aid:3d}] {name[:48]:48s}  FAILED")

        time.sleep(0.2)  # be polite

    print(f"\n=== Summary: {len(success)} ok, {len(failed)} failed ===")
    if failed:
        print("Failed attractions (left as-is, gradient placeholder):")
        for aid, name in failed:
            print(f"  - [{aid}] {name}")
    conn.close()


if __name__ == "__main__":
    main()
