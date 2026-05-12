import ctypes
from ctypes import wintypes
from pathlib import Path

import pyautogui
from PIL import ImageDraw
from PIL.Image import Image

from src.grounder.types import BBox, Viewport

try:
    ctypes.windll.user32.SetProcessDPIAware()
except (AttributeError, OSError):
    pass


def captureScreenshot():
    return pyautogui.screenshot("screen.png")


def get_work_area_viewport() -> Viewport:
    screen_w, screen_h = pyautogui.size()
    full = Viewport(x=0, y=0, width=screen_w, height=screen_h)

    try:
        user32 = ctypes.windll.user32
    except (AttributeError, OSError):
        return full

    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if not hwnd:
        return full

    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return full

    tb_left, tb_top, tb_right, tb_bottom = rect.left, rect.top, rect.right, rect.bottom
    tb_w, tb_h = tb_right - tb_left, tb_bottom - tb_top
    if tb_w <= 0 or tb_h <= 0:
        return full

    if tb_w >= tb_h:
        if tb_top <= 0:
            return Viewport(x=0, y=tb_bottom, width=screen_w, height=screen_h - tb_bottom)
        return Viewport(x=0, y=0, width=screen_w, height=tb_top)
    else:
        if tb_left <= 0:
            return Viewport(x=tb_right, y=0, width=screen_w - tb_right, height=screen_h)
        return Viewport(x=0, y=0, width=tb_left, height=screen_h)


def crop_to_viewport(image: Image, viewport: Viewport) -> Image:
    return image.crop((
        viewport.x,
        viewport.y,
        viewport.x + viewport.width,
        viewport.y + viewport.height,
    ))


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
