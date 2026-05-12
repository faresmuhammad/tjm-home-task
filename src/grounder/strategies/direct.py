from PIL.Image import Image

from src.grounder.providers.base import ModelClient
from src.grounder.roles.grounder import Grounder
from src.grounder.strategies.base import GroundingStrategy
from src.grounder.types import BBox


class DirectStrategy(GroundingStrategy):
    def __init__(self, grounder: Grounder):
        self._grounder = grounder

    def ground(self, image: Image, target_description: str) -> BBox:
        return self._grounder.ground(image, target_description)
