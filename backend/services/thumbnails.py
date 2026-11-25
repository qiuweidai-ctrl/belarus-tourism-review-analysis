from pathlib import Path
import os
from functools import lru_cache
from threading import RLock
from time import monotonic
from urllib.parse import quote, urlparse

from PIL import Image, ImageOps


STATIC_DIR = (Path(__file__).resolve().parents[1] / 'static').resolve()
THUMBNAIL_DIR = STATIC_DIR / 'thumbnails'
THUMBNAIL_LOCK = RLock()


def image_path(url):
    if not url or not url.startswith('/static/'):
        return None
    source = (STATIC_DIR / urlparse(url).path.removeprefix('/static/')).resolve()
    if not source.is_relative_to(STATIC_DIR) or source.is_relative_to(THUMBNAIL_DIR):
        return None
    return source if source.is_file() else None


@lru_cache(maxsize=4096)
def _thumbnail_url(url, width, period):
    source = image_path(url)
    if not source:
        return url
    filename = source.relative_to(STATIC_DIR).as_posix()
    return f'/media/thumbnail/{width}/{quote(filename, safe="/")}?v={source.stat().st_mtime_ns}'


def thumbnail_url(url, width=480):
    return _thumbnail_url(url, width, int(monotonic() // 30))


def clear_thumbnail_cache():
    _thumbnail_url.cache_clear()


def prepare_thumbnail(source, width):
    relative = source.relative_to(STATIC_DIR)
    destination = THUMBNAIL_DIR / str(width) / relative.parent / (relative.name + '.webp')
    # 缩略图按需生成，原图更新后会重新生成。
    with THUMBNAIL_LOCK:
        if not destination.exists() or destination.stat().st_mtime_ns < source.stat().st_mtime_ns:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as original:
                image = ImageOps.exif_transpose(original).convert('RGB')
                image.thumbnail((width, width), Image.Resampling.LANCZOS)
                temporary = destination.with_suffix(f'.{os.getpid()}.tmp')
                try:
                    image.save(temporary, 'WEBP', quality=80, method=4)
                    temporary.replace(destination)
                finally:
                    temporary.unlink(missing_ok=True)
    return destination
