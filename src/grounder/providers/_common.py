import base64
import json
from io import BytesIO

from PIL.Image import Image

from src.log import logger


def encode_image_b64(image: Image, format: str = "PNG") -> str:
    buffer = BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def extract_json(text: str) -> dict:
    if not text:
        return {}

    text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error(f"Invalid Json: {text}")
        raise Exception("Invalid Json Response")
