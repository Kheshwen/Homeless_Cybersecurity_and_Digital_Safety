import easyocr
import io
from PIL import Image
import numpy as np

# Load the model globally at startup because the first load is slow
reader = easyocr.Reader(['en', 'ms'])

def extract_text_from_image(image_bytes: bytes) -> str:
    """Reads image bytes, runs OCR, and merges output into one text string."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)
    
    results = reader.readtext(image_np, detail=0)
    return " ".join(results)