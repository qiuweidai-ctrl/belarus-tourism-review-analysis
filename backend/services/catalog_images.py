from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parents[1]
MIN_WIDTH, MIN_HEIGHT = 160, 120


# 发布前确认图片在static目录中，并且能正常打开。
def local_image_metadata(url, base_dir=BASE_DIR):
    if not isinstance(url, str) or not url.startswith('/static/'):
        return None
    root = (base_dir / 'static').resolve()
    path = (base_dir / url.lstrip('/')).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return None
    try:
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return None
        return {
            'width': width, 'height': height, 'bytes': path.stat().st_size,
        }
    except (OSError, ValueError, Image.DecompressionBombError):
        return None
