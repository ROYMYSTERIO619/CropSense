import numpy as np
from PIL import Image
import io


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Full preprocessing pipeline for incoming leaf images.
    1. Load from bytes
    2. Convert to RGB (handle RGBA, grayscale)
    3. Resize to 224x224 with LANCZOS resampling
    4. Normalize to [0, 1]
    5. Expand dims for batch
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize((224, 224), Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(img_array, axis=0)


def validate_image(image_bytes: bytes) -> bool:
    """Check if uploaded file is a valid image."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True
    except Exception:
        return False
