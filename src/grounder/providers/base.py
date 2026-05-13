from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import sleep
from typing import Optional

from PIL.Image import Image

from src.log import logger


@dataclass
class ModelRequest:
    prompt: str
    image: Optional[Image] = None


@dataclass
class ModelResponse:
    text: str
    parsed_json: dict | list


class ModelClient(ABC):

    @abstractmethod
    def instantiate_client(self):
        """Setup Client Instance"""
        
    @abstractmethod
    def send_api(self, request: ModelRequest) -> ModelResponse:
        """Send API Call"""

    def execute(self, request: ModelRequest, tries: int = 3) -> ModelResponse:
        self.instantiate_client()

        if request.image is None:
            logger.error("Image is empty")
            raise Exception("Image is required")

        last_err: Optional[Exception] = None
        for t in range(tries):
            logger.info(f"{type(self).__name__} Try: {t+1}/{tries}")
            try:
                return self.send_api(request)
            except Exception as e:
                last_err = e
                logger.error(f"{type(self).__name__} Try {t+1}/{tries} failed: {e}")
                sleep(1)

        raise RuntimeError(
            f"{type(self).__name__} exhausted {tries} retries"
        ) from last_err
