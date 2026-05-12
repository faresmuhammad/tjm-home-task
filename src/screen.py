from pathlib import Path

import pyautogui
from PIL import ImageDraw
from PIL.Image import Image

from src.grounder.types import BBox


def captureScreenshot():
    return pyautogui.screenshot("screen.png")


def save_annotated_screenshot(
    image: Image,
    bbox: BBox,
    output_path: Path,
    outline_color: str = "red",
    width: int = 4,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    draw.rectangle([bbox.x1, bbox.y1, bbox.x2, bbox.y2], outline=outline_color, width=width)
    cx, cy = bbox.center
    r = 6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=outline_color, width=width)
    annotated.save(output_path)
    return output_path


def navigateToDesktop():
    pyautogui.hotkey("win", "m")


def moveTo(x, y, interval=0.0):
    pyautogui.moveTo(x, y, interval)


def doubleClick(x=None, y=None, interval=0.0):
    pyautogui.doubleClick(x, y, interval)
