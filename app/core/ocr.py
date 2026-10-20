import io

_reader = None


def _get_reader():
    """Loads EasyOCR on first use (slow, and heavy to import), not at app startup."""
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en", "ms"])
    return _reader


def extract_text_from_image(image_bytes: bytes) -> str:
    """Reads image bytes, runs OCR, and merges output into one text string."""
    import numpy as np
    from PIL import Image

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = _get_reader().readtext(np.array(image), detail=0)
    return " ".join(results)
