import base64
import json
import re
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

    # Direct Parse
    text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error(f"Invalid Json on direct parsing: {text}")
        pass

    # If response is fenced with ```json ...```
    reg = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = reg.search(text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            logger.error(f"Invalid Json on fenced: {text}")
            pass
            