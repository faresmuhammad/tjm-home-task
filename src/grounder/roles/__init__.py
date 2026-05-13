
from abc import ABC
from dataclasses import dataclass
import logging

from src.grounder.providers.base import ModelClient
from src.grounder.types import BBox

logger = logging.getLogger(__name__)

def _denorm_bbox(
    normalized: list[float] | list[int],
    image_size: tuple[int, int],
    norm_max: float = 1000.0,
) -> BBox:

    if len(normalized) != 4:
        raise ValueError(f"Expected 4 coordinates, got {len(normalized)}: {normalized}")
    w, h = image_size
    x1, y1, x2, y2 = normalized
    # Auto-detect 0..1 vs 0..1000 convention
    if max(abs(v) for v in normalized) <= 1.0:
        scale_x, scale_y = w, h
    else:
        scale_x, scale_y = w / norm_max, h / norm_max
    # Clip to valid range and round to ints
    px = lambda v, scale, dim: max(0, min(dim - 1, int(round(v * scale))))
    return BBox(
        x1=px(x1, scale_x, w),
        y1=px(y1, scale_y, h),
        x2=px(x2, scale_x, w),
        y2=px(y2, scale_y, h),
    )


class TargetNotVisibleError(Exception):
    """Raised when all grounding providers agree the target is not in the image."""

@dataclass
class CandidateRegion:
    description: str
    bbox: BBox
    neighbors: list[str]

@dataclass
class PlannerOutput:
    regions: list[CandidateRegion]
    reason: str = ""

@dataclass
class GroundResult:
    bbox: BBox

class Role(ABC):
    def __init__(self, clients: ModelClient | list[ModelClient]) -> None:
        self._clients: list[ModelClient] = (
            clients if isinstance(clients, list) else [clients]
        )