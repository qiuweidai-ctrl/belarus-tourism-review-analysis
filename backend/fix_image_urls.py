# -*- coding: utf-8 -*-
"""
One-shot fix: re-point every attraction's image_url to the bundled
local file (/static/images/attractions/{id}.jpg).

The image files were downloaded by fetch_images.py, but the database
was left with Wikipedia URLs. When the client machine cannot reach
Wikipedia (firewall / DNS), the frontend shows broken images.

Run:  python fix_image_urls.py
"""
import os
import pymysql

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "static", "images", "attractions")

print(f"Image directory: {IMG_DIR}")
if not os.path.isdir(IMG_DIR):
    print("ERROR: image directory not found.")
    raise SystemExit(1)

on_disk = {
    int(os.path.splitext(f)[0])
    for f in os.listdir(IMG_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
}
print(f"Images found on disk: {len(on_disk)}")

conn = pymysql.connect(host="localhost", user="root", password="123456",
                       database="belarus_tourism", charset="utf8mb4")
cur = conn.cursor()

cur.execute("SELECT id, name, image_url FROM attractions")
rows = cur.fetchall()
print(f"Attractions in DB: {len(rows)}")

local_rel = lambda aid: f"/static/images/attractions/{aid}.jpg"

updated, missing, already_local = 0, [], 0
for aid, name, image_url in rows:
    if image_url == local_rel(aid):
        already_local += 1
        continue
    if aid in on_disk:
        cur.execute("UPDATE attractions SET image_url=%s WHERE id=%s",
                    (local_rel(aid), aid))
        updated += 1
    else:
        missing.append((aid, name))

conn.commit()
print(f"\n=== Summary ===")
print(f"  Already local:    {already_local}")
print(f"  Updated → local:  {updated}")
print(f"  No image on disk: {len(missing)}")
for aid, name in missing[:10]:
    print(f"     - [{aid}] {name}")

cur.close()
conn.close()
print("\nDone. Restart the backend so SQLAlchemy clears its session cache.")