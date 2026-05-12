
DIRECT_GROUND_PROMPT = """You are a GUI grounding assistant. Locate the target element on the screenshot.

TARGET: {target_description}

Return its bounding box in normalized coordinates 0-1000, where (0,0) is top-left and (1000,1000) is bottom-right of the image.

Respond with JSON only:
{{"bbox": [x1, y1, x2, y2]}}

If the target is NOT visible, respond:
{{"bbox": null}}"""


def direct_ground_prompt(target_description: str) -> str:
    return DIRECT_GROUND_PROMPT.format(target_description=target_description)