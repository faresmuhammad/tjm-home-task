
DIRECT_GROUND_PROMPT = """You are a GUI grounding assistant. Locate the target element and its similar on the screenshot.

TARGET: {target_description}

Return their bounding boxes in normalized coordinates 0-1000, where (0,0) is top-left and (1000,1000) is bottom-right of the image.

Respond with JSON only:
{{
    "boxes": [
        {{"bbox": [x1, y1, x2, y2]}}
        ...
    ]
}}

If the target is NOT visible or any similar, respond:
{{
    "boxes": []
}}"""


def direct_ground_prompt(target_description: str) -> str:
    return DIRECT_GROUND_PROMPT.format(target_description=target_description)


PLAN_REGIONS_PROMPT = """You are a GUI navigation planner. Identify the most likely regions of the screen where a target element appears.

TARGET: {target_description}

Output requirements:
1. List up to 3 candidate regions in DESCENDING order of probability.
2. Each region must be specific and uniquely identifiable. "Toolbar" is too vague; "top toolbar in the File Explorer window" is specific.
3. For each region, name 1-3 neighboring elements likely to appear next to the target (e.g. "next to the New button").

Respond with JSON only:
{{
  "regions": [
    {{
      "description": "<specific region>",
      "bbox": [x1, y1, x2, y2],
      "neighbors": ["<neighbor 1>", "<neighbor 2>"]
    }},
    ...
  ]
}}

Coordinates are normalized 0-1000. If the target clearly does not exist in this screenshot, respond:
{{"regions": [], "reason": "<why not found>"}}"""


def plan_regions_prompt(target_description: str) -> str:
    return PLAN_REGIONS_PROMPT.format(target_description=target_description)

VERIFY_PROMPT = """You are a GUI verification assistant. The provided image is a cropped region from a larger screenshot. Determine whether the target element is visible in this crop.

TARGET: {target_description}

Respond with JSON only:
{{"verdict": "<is_target | not_found>"}}

Verdicts:
  - "is_target": the target is clearly visible in this crop
  - "not_found": the target is not in this crop"""


def verify_prompt(target_description: str) -> str:
    return VERIFY_PROMPT.format(target_description=target_description)
