# -*- coding: utf-8 -*-
"""
Belarus Tourism Data Scraper
============================
Scrapes Belarus tourist attractions from:
  1. Wikidata SPARQL endpoint   → structured facts (name, coords, category, image)
  2. Wikipedia REST API         → rich descriptions & extracts
  3. Wikimedia Commons API      → high-quality images

Usage:
    python scrape_wikidata.py          # full pipeline
    python scrape_wikidata.py --dry-run   # preview only, no DB write
    python scrape_wikidata.py --limit 20   # cap at N results
    python scrape_wikidata.py --skip-images  # skip image downloads

Dependencies:
    pip install requests

Run from: belarus-tourism/backend/
"""
import os, sys, json, time, argparse
import requests
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
DRY_RUN        = False
HEADERS        = {
    "User-Agent": "BelarusTourismBot/1.0 (Python/requests; educational project; belarus-tourism@example.com)"
}
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATA_OUT       = os.path.join(BASE_DIR, "scraped_data.json")
IMAGES_OUT_DIR = os.path.join(BASE_DIR, "static", "images")
os.makedirs(IMAGES_OUT_DIR, exist_ok=True)

WD_SPARQL   = "https://query.wikidata.org/sparql"
WD_API      = "https://www.wikidata.org/w/api.php"
WK_API      = "https://en.wikipedia.org/api/rest_v1"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# ── SPARQL query ──────────────────────────────────────────────────────────────
# Belarus attractions: castle, church, museum, memorial, palace, nature, etc.
WD_QUERY = """
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd:  <http://www.wikidata.org/entity/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?item ?itemLabel ?coords ?image ?commons
WHERE {
  ?item wdt:P17 wd:Q184 .
  ?item (wdt:P31/(wdt:P279*)) ?type .
  VALUES ?type {
    wd:Q41176      wd:Q450953      wd:Q12772198   # castle, fortified castle, castle ruins
    wd:Q22698      wd:Q207338      wd:Q10382399   # museum, history museum, art museum
    wd:Q167402     wd:Q2977        wd:Q16970       # church, cathedral, basilica
    wd:Q16742      wd:Q4804279     wd:Q489817     # monastery, convent, abbey
    wd:Q42884      wd:Q913435      wd:Q721747     # memorial, monument, war memorial
    wd:Q166850     wd:Q590102      wd:Q43876      # national park, nature reserve, protected area
    wd:Q50337      wd:Q350460      wd:Q188509     # park, botanical garden, lake, river, waterfall
    wd:Q35509      wd:Q56012       wd:Q511056     # public building, library, notable building
    wd:Q1532822    wd:Q108113888                # biosphere reserve, natural site
    wd:Q1752368    wd:Q1320428                   # observation tower, historic building
    wd:Q570116                                  # tourist attraction (catch-all)
  }
  FILTER EXISTS { ?item rdfs:label ?itemLabel FILTER(LANG(?itemLabel)="en") }
  FILTER EXISTS { ?item wdt:P625 ?coords }

  ?item rdfs:label ?itemLabel FILTER(LANG(?itemLabel)="en")
  OPTIONAL { ?item wdt:P625 ?coords }
  OPTIONAL { ?item wdt:P18 ?image }
  OPTIONAL { ?item schema:about ?commons
             FILTER(CONTAINS(STR(?commons), "commons.wikimedia.org")) }
}
LIMIT 500
"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def sparql_query(query: str, retry=3) -> list:
    for attempt in range(retry):
        try:
            resp = requests.get(
                WD_SPARQL,
                params={"query": query, "format": "json"},
                headers=HEADERS,
                timeout=90
            )
            resp.raise_for_status()
            return resp.json().get("results", {}).get("bindings", [])
        except Exception as e:
            wait = 2 ** attempt
            print(f"  [SPARQL] attempt {attempt+1} failed: {e} — sleeping {wait}s")
            time.sleep(wait)
    return []


def resolve_coords(raw: str):
    """Parse 'Point(lon lat)' → (lat, lon)."""
    if not raw:
        return None, None
    try:
        inner = raw.replace("Point(", "").replace(")", "")
        lon, lat = inner.split()
        return round(float(lat), 6), round(float(lon), 6)
    except Exception:
        return None, None


def wikidata_entity_batch(qids: list) -> dict:
    """Fetch labels for a batch of QIDs in one API call."""
    if not qids:
        return {}
    try:
        resp = requests.get(
            WD_API,
            params={
                "action": "wbgetentities",
                "ids": "|".join(qids),
                "props": "labels",
                "languages": "en",
                "format": "json",
            },
            headers=HEADERS,
            timeout=30
        )
        resp.raise_for_status()
        entities = resp.json().get("entities", {})
        result = {}
        for qid, ent in entities.items():
            result[qid] = ent.get("labels", {}).get("en", {}).get("value", "")
        return result
    except Exception as e:
        print(f"  [WD-BATCH] error: {e}")
        return {}


def wikidata_full(item_uri: str) -> dict:
    """Fetch full entity data: labels, descriptions, types, location, heritage."""
    qid = item_uri.split("/")[-1]
    for attempt in range(4):
        try:
            resp = requests.get(
                WD_API,
                params={
                    "action": "wbgetentities",
                    "ids": qid,
                    "props": "labels|descriptions|claims",
                    "languages": "en|be",
                    "format": "json",
                },
                headers=HEADERS,
                timeout=20,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 5))
                print(f"  [WD 429] sleeping {retry_after}s")
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
            break
        except Exception as e:
            wait = 2 ** attempt
            print(f"  [WD] attempt {attempt+1} failed: {e} — retry in {wait}s")
            time.sleep(wait)
    else:
        return {}

    try:
        entity = resp.json().get("entities", {}).get(qid, {})
        if not entity or "claims" not in entity:
            return {}
        claims = entity.get("claims", {})

        def get_prop(pid):
            out = []
            for v in claims.get(pid, []):
                dv = (v.get("mainsnak") or {}).get("datavalue")
                if not dv:
                    continue
                typ = dv.get("type", "")
                if typ == "wikibase-entityid":
                    out.append(dv["value"]["id"])
                elif typ in ("string", "external-id", "url"):
                    out.append(str(dv["value"]))
            return out

        def get1(pid):
            vals = get_prop(pid)
            return vals[0] if vals else None

        # Batch-fetch type labels
        type_qids = get_prop("P31")[:4]
        type_map = wikidata_entity_batch(type_qids)
        type_labels = [v for v in (type_map.get(q) for q in type_qids) if v]
        type_labels_lower = [t.lower() for t in type_labels]

        # Region
        region_qid = get1("P131")
        region_name = ""
        if region_qid:
            region_map = wikidata_entity_batch([region_qid])
            region_name = region_map.get(region_qid, "")

        return {
            "qid": qid,
            "name_en": entity.get("labels", {}).get("en", {}).get("value", ""),
            "name_be": entity.get("labels", {}).get("be", {}).get("value", ""),
            "description": entity.get("descriptions", {}).get("en", {}).get("value", ""),
            "type_labels": type_labels_lower,
            "region_qid": region_qid,
            "region_name": region_name,
            "heritage_qid": get1("P1435"),
            "website": get1("P856"),
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}",
        }
    except Exception as e:
        print(f"  [WD] parse error: {e}")
        return {}


def wikipedia_extract(title: str) -> dict:
    """Fetch summary + thumbnail from Wikipedia REST API."""
    try:
        resp = requests.get(
            f"{WK_API}/page/summary/{requests.utils.quote(title)}",
            headers=HEADERS, timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "extract":     data.get("extract", ""),
            "description": data.get("description", ""),
            "thumbnail":   (data.get("thumbnail") or {}).get("source", ""),
            "page_url":    (data.get("content_urls", {}).get("desktop", {}) or {}).get("page", ""),
        }
    except Exception as e:
        print(f"  [WK] error for '{title}': {e}")
        return {}


def wikipedia_full(title: str) -> str:
    """Fetch full article text from Wikipedia parse API."""
    try:
        resp = requests.get(
            WD_API,
            params={
                "action": "query",
                "titles": title,
                "prop": "extracts",
                "exintro": False,
                "explaintext": True,
                "format": "json",
            },
            headers=HEADERS, timeout=15
        )
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for pg in pages.values():
            return pg.get("extract", "")
    except Exception:
        return ""


def download_image(filename: str, out_dir: str, max_w: int = 800) -> str:
    """Download a Wikimedia Commons image; return local path or ''."""
    try:
        resp = requests.get(
            COMMONS_API,
            params={
                "action": "query",
                "titles": f"File:{filename}",
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": max_w,
                "format": "json",
            },
            headers=HEADERS, timeout=20
        )
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for pg in pages.values():
            info = (pg.get("imageinfo") or [{}])[0]
            img_url = info.get("thumburl") or info.get("url", "")
            if not img_url:
                continue
            img_data = requests.get(img_url, headers=HEADERS, timeout=30)
            img_data.raise_for_status()
            safe = filename.replace("/", "_").replace(" ", "_")
            path = os.path.join(out_dir, safe)
            with open(path, "wb") as f:
                f.write(img_data.content)
            return path
    except Exception as e:
        print(f"  [IMG] failed {filename}: {e}")
    return ""


def infer_category(types: list) -> str:
    """Map Wikidata type labels → our category enum."""
    mapping = [
        (["castle", "ruins", "fort"],       "castle"),
        (["museum", "gallery", "exhibition"], "museum"),
        (["church", "cathedral", "monastery", "abbey", "chapel", "temple", "convent"], "church"),
        (["memorial", "monument", "war memorial"], "memorial"),
        (["national park", "nature reserve", "protected area", "biosphere", "nature",
          "lake", "river", "waterfall", "botanical garden", "forest"], "nature"),
        (["palace", "manor", "estate", "mansion"], "palace"),
        (["park", "garden", "zoo", "aquarium"], "park"),
        (["public building", "library", "theatre", "theater", "station",
          "observation tower", "skyline"], "architecture"),
    ]
    for keywords, cat in mapping:
        if any(kw in " ".join(types) for kw in keywords):
            return cat
    return "other"


def infer_season(category: str) -> str:
    return {
        "nature":    "Spring, Summer, Autumn",
        "park":      "Spring, Summer, Autumn",
        "castle":    "Spring, Summer, Autumn",
        "palace":    "Spring, Summer, Autumn",
        "church":    "All seasons",
        "memorial":  "All seasons",
        "museum":    "All seasons",
        "architecture": "All seasons",
    }.get(category, "All seasons")


def build_description(item: dict) -> str:
    parts = []
    if item.get("wiki_extract"):
        parts.append(item["wiki_extract"][:1000].strip())
    if item.get("wiki_description") and item["wiki_description"] not in (item.get("wiki_extract") or ""):
        parts.append(f"({item['wiki_description']})")
    heritage = item.get("heritage_name", "")
    if heritage:
        parts.append(f"Heritage: {heritage}.")
    site = item.get("website", "")
    if site:
        parts.append(f"More info: {site}")
    return " ".join(parts).strip()


def build_short_desc(item: dict) -> str:
    cat_names = {
        "castle": "castle", "church": "church", "memorial": "memorial",
        "museum": "museum", "nature": "nature site", "palace": "palace & estate",
        "park": "park & garden", "architecture": "architectural landmark",
    }
    cat_str = cat_names.get(item["category"], "tourist attraction")
    region = item.get("region_name", "")
    loc = f" in {region}" if region else ""
    return f"{item.get('name_en', '')} — {cat_str}{loc}."


# ── Phase 1: Wikidata SPARQL ─────────────────────────────────────────────────

def phase1_wikidata() -> list:
    print("\n=== Phase 1: Wikidata SPARQL ===")
    raw = sparql_query(WD_QUERY)
    print(f"  Raw bindings: {len(raw)}")

    # Deduplicate
    seen, items = set(), []
    for row in raw:
        uri = row.get("item", {}).get("value", "")
        if uri and uri not in seen:
            seen.add(uri)
            items.append(row)

    print(f"  Deduplicated: {len(items)}")

    # Batch process entity lookups (rate-limiting safe: 1 call per 3 items)
    results = []
    total = len(items)
    for i, row in enumerate(items):
        uri = row["item"]["value"]
        label = row.get("itemLabel", {}).get("value", "")
        print(f"  [{i+1}/{total}] {label[:50]}...", end=" ", flush=True)

        lat, lon = resolve_coords(row.get("coords", {}).get("value", ""))
        raw_img = row.get("image", {}).get("value", "")
        filename = os.path.basename(raw_img) if raw_img else ""

        entity = wikidata_full(uri)
        time.sleep(0.35)  # Wikidata rate limit: ~1 req/sec is safe

        region_name = entity.get("region_name", "")

        results.append({
            "wikidata_uri": uri,
            "qid":          entity.get("qid", uri.split("/")[-1]),
            "name_en":      label or entity.get("name_en", ""),
            "name_be":      entity.get("name_be", ""),
            "wiki_description": entity.get("description", ""),
            "category_raw": entity.get("type_labels", []),
            "category":     infer_category(entity.get("type_labels", [])),
            "latitude":     lat,
            "longitude":    lon,
            "region_qid":   entity.get("region_qid", ""),
            "region_name":  region_name,
            "heritage_qid": entity.get("heritage_qid", ""),
            "heritage_name": "",
            "website":      entity.get("website", ""),
            "wikidata_url": entity.get("wikidata_url", ""),
            "image_filename": filename,
            "wiki_extract":    "",
            "wiki_thumbnail":   "",
            "wiki_page_url":    "",
            "local_image_path": "",
            "scraped_at": datetime.utcnow().isoformat(),
        })
        print("OK")

    return results


# ── Phase 2: Wikipedia enrichment ────────────────────────────────────────────

def phase2_wikipedia(items: list):
    print("\n=== Phase 2: Wikipedia enrichment ===")
    for i, item in enumerate(items):
        title = item["name_en"]
        print(f"  [{i+1}/{len(items)}] {title[:50]}...", end=" ", flush=True)

        summary = wikipedia_extract(title)
        if summary:
            item["wiki_extract"]    = summary.get("extract", "")
            item["wiki_description"] = summary.get("description", "")
            item["wiki_thumbnail"]  = summary.get("thumbnail", "")
            item["wiki_page_url"]   = summary.get("page_url", "")
            print("OK")
        else:
            item["wiki_extract"]    = ""
            item["wiki_description"] = ""
            print("SKIP")

        # Fallback: try full content if extract is tiny
        if not item.get("wiki_extract") or len(item["wiki_extract"]) < 80:
            full = wikipedia_full(title)
            if len(full) > 100:
                item["wiki_extract"] = full[:2000]
                print("(full article)")

        time.sleep(0.2)


# ── Phase 3: Download images ─────────────────────────────────────────────────

def phase3_images(items: list):
    print(f"\n=== Phase 3: Images → {IMAGES_OUT_DIR} ===")
    for i, item in enumerate(items):
        fname = item.get("image_filename", "")
        if not fname:
            item["local_image_path"] = ""
            continue
        print(f"  [{i+1}/{len(items)}] {fname[:55]}...", end=" ", flush=True)
        local = download_image(fname, IMAGES_OUT_DIR, max_w=800)
        item["local_image_path"] = local
        print("OK" if local else "SKIP")
        time.sleep(0.3)


# ── Phase 4: Write to MySQL ─────────────────────────────────────────────────

def phase4_db(items: list):
    print("\n=== Phase 4: MySQL DB update ===")
    if DRY_RUN:
        print("  [DRY RUN] DB writes skipped")
        return

    sys.path.insert(0, BASE_DIR)
    from app import create_app
    from models import db, Attraction

    app = create_app()
    with app.app_context():
        existing = {a.name_en.lower(): a for a in Attraction.query.all()}

        added = updated = skipped = 0
        for item in items:
            name = item["name_en"]
            if not name:
                skipped += 1
                continue

            # Resolve heritage name
            heritage_qid = item.get("heritage_qid", "")
            if heritage_qid:
                hmap = wikidata_entity_batch([heritage_qid])
                item["heritage_name"] = hmap.get(heritage_qid, "")

            short_desc  = build_short_desc(item)
            description  = build_description(item)

            # Local image path → static URL
            local_img = item.get("local_image_path", "")
            image_url = ""
            if local_img and os.path.exists(local_img):
                image_url = f"/static/images/{os.path.basename(local_img)}"
            elif item.get("wiki_thumbnail", ""):
                image_url = item["wiki_thumbnail"]

            city = item["region_name"].split()[0] if item["region_name"] else ""

            att = existing.get(name.lower())
            if att:
                # Update only empty fields (preserve user data)
                if not att.description or len(description) > len(att.description or ""):
                    att.description = description
                if not att.short_desc:
                    att.short_desc = short_desc
                if not att.image_url and image_url:
                    att.image_url = image_url
                if not att.latitude and item.get("latitude"):
                    att.latitude = item["latitude"]
                if not att.longitude and item.get("longitude"):
                    att.longitude = item["longitude"]
                if not att.region and item["region_name"]:
                    att.region = item["region_name"]
                if not att.city and city:
                    att.city = city
                if not att.name_be and item.get("name_be"):
                    att.name_be = item["name_be"]
                if not att.suitable_season:
                    att.suitable_season = infer_season(item["category"])
                att.is_verified  = True
                att.updated_at   = datetime.utcnow()
                updated += 1
                print(f"  [UPDATE] {name}")
            else:
                att = Attraction(
                    name          = name,
                    name_en       = name,
                    name_be       = item.get("name_be", ""),
                    description    = description,
                    short_desc     = short_desc,
                    location       = item["region_name"] or "Belarus",
                    city           = city,
                    region         = item["region_name"],
                    latitude       = item.get("latitude"),
                    longitude      = item.get("longitude"),
                    category       = item["category"],
                    suitable_season= infer_season(item["category"]),
                    opening_hours  = "",
                    ticket_price   = 0.00,
                    image_url      = image_url,
                    avg_rating     = 0.00,
                    total_reviews  = 0,
                    is_verified    = True,
                    is_featured    = False,
                    created_by     = None,
                )
                db.session.add(att)
                added += 1
                print(f"  [NEW] {name}")

            db.session.commit()

    print(f"\n  Done: {added} added, {updated} updated, {skipped} skipped")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Belarus Tourism Scraper")
    ap.add_argument("--dry-run",      action="store_true", help="Preview only, no DB writes")
    ap.add_argument("--limit",        type=int, default=0,   help="Max items (0=unlimited)")
    ap.add_argument("--skip-images",  action="store_true", help="Skip image downloads")
    ap.add_argument("--output",       default=DATA_OUT,      help="JSON output path")
    args = ap.parse_args()

    global DRY_RUN
    DRY_RUN = args.dry_run

    print("=" * 55)
    print(" Belarus Tourism Scraper")
    print("=" * 55)
    if DRY_RUN:
        print("  [DRY RUN mode — no DB writes]")
    print()

    # Phase 1
    items = phase1_wikidata()

    if args.limit > 0:
        items = items[:args.limit]
        print(f"\n  Limited to {args.limit} items")

    # Phase 2
    phase2_wikipedia(items)

    # Phase 3
    if not args.skip_images:
        phase3_images(items)
    else:
        print("\n=== Phase 3: SKIPPED ===")

    # Save JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n  Data saved → {args.output}")

    # Phase 4
    phase4_db(items)

    print("\n" + "=" * 55)
    print(" Done!")
    print("=" * 55)


if __name__ == "__main__":
    main()
