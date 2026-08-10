import time
print(f">>> ocr.py   starting [{time.perf_counter():.3f}]")

from PIL import Image, ImageEnhance
import numpy as np

from logger import log

_reader = None


def get_reader():
    global _reader

    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['en'], gpu=False)

    return _reader

def ocr_image(filename, region=None, allowlist=None, detail=0):
    """OCR sobre una imagen guardada, opcionalmente recortando una región."""
    with Image.open(filename) as photo:
        if region:
            photo = photo.crop(region)
        photo = photo.convert("L")
        photo = ImageEnhance.Contrast(photo).enhance(2.0)
        image_np = np.array(photo)

    try:
        reader = get_reader()
        return reader.readtext(image_np, allowlist=allowlist, detail=detail)
    except Exception as e:
        log(f"[OCR] Error procesando imagen {filename}: {e}")
        return []
