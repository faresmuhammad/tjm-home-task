from PIL.Image import Image

from src.grounder.roles import GroundResult
from src.grounder.roles.grounder import Grounder
from src.grounder.strategies.base import GroundingStrategy


class DirectStrategy(GroundingStrategy):
    def __init__(self, grounder: Grounder):
        self._grounder = grounder

    def ground(self, image: Image, target_description: str) -> GroundResult:
        return self._grounder.ground(image, target_description)
