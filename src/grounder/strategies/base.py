
from abc import ABC, abstractmethod

from PIL.Image import Image

from src.grounder.types import BBox


class GroundingStrategy(ABC):

    @abstractmethod
    def ground(self,image: Image,target_description:str) -> BBox:
        """Locate a stragey, and return GroundingResult"""