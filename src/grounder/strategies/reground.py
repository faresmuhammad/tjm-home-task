from PIL.Image import Image

from src.grounder.roles import GroundResult
from src.grounder.roles.grounder import Grounder
from src.grounder.strategies.base import GroundingStrategy
from src.grounder.types import Viewport


class RegroundStrategy(GroundingStrategy):
    def __init__(self, grounder: Grounder, crop_size: int = 1024):
        self._grounder = grounder
        self._crop_size = crop_size

    def ground(self, image: Image, target_description: str) -> GroundResult:
        # first direct ground
        screen_w, screen_h = image.size
        first_ground = self._grounder.ground(image, target_description)
        cx, cy = first_ground.bbox.center

        half_crop_size = self._crop_size // 2
        x0 = min(0, max(cx - half_crop_size, screen_w - self._crop_size))
        y0 = min(0, max(cy - half_crop_size, screen_h - self._crop_size))
        x1 = min(screen_w, x0 + self._crop_size)
        y1 = min(screen_h, y0 + self._crop_size)

        crop_viewport = Viewport(x=x0, y=y0, width=x1 - x0, height=y1 - y0)
        crop = image.crop((x0, y0, x1, y1))

        second_ground = self._grounder.ground(crop, target_description)

        return GroundResult(bbox=crop_viewport.to_screen(second_ground.bbox))
