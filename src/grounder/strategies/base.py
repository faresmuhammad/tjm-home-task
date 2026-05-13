
from abc import ABC, abstractmethod

from PIL.Image import Image

from src.grounder.roles import GroundResult


class GroundingStrategy(ABC):

    @abstractmethod
    def ground(self, image: Image, target_description: str) -> GroundResult:
        """Locate a strategy, and return GroundResult"""
