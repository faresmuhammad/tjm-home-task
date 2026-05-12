from PIL.Image import Image

from src.grounder.prompts import direct_ground_prompt
from src.grounder.providers.base import ModelClient, ModelRequest
from src.grounder.types import BBox


def _denorm_bbox(
    normalized: list[float] | list[int],
    image_size: tuple[int, int],
    norm_max: float = 1000.0,
) -> BBox:
    """Convert [x1, y1, x2, y2] in 0..norm_max to pixel coordinates.

    Models trained on grounding (Gemini, Qwen-VL) typically output in
    0..1000 normalized space. This converter handles both the 0..1 and
    0..1000 conventions — auto-detected by checking if all values ≤ 1.
    """
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


class Grounder:
    def __init__(self, clients: ModelClient | list[ModelClient]) -> None:
        self._clients: list[ModelClient] = (
            clients if isinstance(clients, list) else [clients]
        )

    def ground(self, image: Image, target_description: str) -> BBox:
        prompt = direct_ground_prompt(target_description)
        total = len(self._clients)
        last_err: Exception | None = None
        null_votes = 0
        errored = 0

        for i, client in enumerate(self._clients):
            try:
                response = client.execute(ModelRequest(prompt, image))
                parsed = response.parsed_json or {}
                bbox_raw = parsed.get("bbox")

                if bbox_raw is None:
                    null_votes += 1
                    last_err = ValueError("Target not visible")
                    print(
                        f"[Grounder] client {i+1}/{total} "
                        f"({type(client).__name__}) reported target not visible"
                    )
                    continue

                try:
                    return _denorm_bbox(bbox_raw, image.size)
                except Exception:
                    raise TypeError("Couldn't parse bbox")
            except Exception as e:
                errored += 1
                print(
                    f"[Grounder] client {i+1}/{total} "
                    f"({type(client).__name__}) failed: {e}"
                )
                last_err = e

        if null_votes > 0 and null_votes + errored == total:
            raise TargetNotVisibleError(
                f"{null_votes}/{total} providers reported target not visible "
                f"({errored} errored)"
            )

        raise RuntimeError(
            f"All {total} grounding providers exhausted"
        ) from last_err
        
