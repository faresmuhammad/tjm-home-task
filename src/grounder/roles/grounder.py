from PIL.Image import Image

from src.grounder.prompts import direct_ground_prompt
from src.grounder.providers.base import ModelClient, ModelRequest
from src.grounder.roles import (
    GroundResult,
    Role,
    TargetNotVisibleError,
    _denorm_bbox,
    logger,
)
from src.grounder.types import BBox

VERIFY_CROP_SIZE = 200
MAX_DEPTH = 2


class Grounder(Role):
    def __init__(self, clients: ModelClient | list[ModelClient]) -> None:
        super().__init__(clients)

    def ground(
        self,
        image: Image,
        target_description: str,
        _depth: int = 0,
    ) -> GroundResult:
        prompt = direct_ground_prompt(target_description)
        total = len(self._clients)
        last_err: Exception | None = None
        null_votes = 0
        errored = 0

        for i, client in enumerate(self._clients):
            try:
                response = client.execute(ModelRequest(prompt, image))
                parsed = response.parsed_json or {}
                raw_boxes = parsed.get("boxes", [])

                candidates: list[BBox] = []
                for entry in raw_boxes:
                    bbox_raw = entry.get("bbox") if isinstance(entry, dict) else None
                    if not bbox_raw:
                        continue
                    try:
                        candidates.append(_denorm_bbox(bbox_raw, image.size))
                    except (ValueError, TypeError):
                        continue

                if not candidates:
                    null_votes += 1
                    last_err = ValueError("Target not visible")
                    logger.error(
                        f"client {i + 1}/{total} "
                        f"({type(client).__name__}) reported target not visible"
                    )
                    continue

                if len(candidates) == 1:
                    logger.info(f"Single Candidate Detected: {candidates[0]}")
                    return GroundResult(bbox=candidates[0])

                logger.info(
                    f"client {i + 1}/{total} "
                    f"({type(client).__name__}) returned {len(candidates)} candidates; "
                    f"verifying by label (depth={_depth})"
                )
                logger.info(f"candidates are: {candidates}")

                if _depth >= MAX_DEPTH:
                    null_votes += 1
                    last_err = TargetNotVisibleError(
                        "max verification depth reached without unique target"
                    )
                    continue

                verified = self._verify_candidates(
                    image, candidates, target_description, _depth
                )
                if verified is not None:
                    logger.info(f"verified bbox: {verified}")
                    return GroundResult(bbox=verified)

                null_votes += 1
                last_err = TargetNotVisibleError(
                    "no candidate passed label verification"
                )
            except TargetNotVisibleError as e:
                logger.error(f"Detection Failed: {e}")
                raise
            except Exception as e:
                errored += 1
                logger.error(
                    f"client {i + 1}/{total} "
                    f"({type(client).__name__}) failed: {e}"
                )
                last_err = e

        if null_votes > 0 and null_votes + errored == total:
            raise TargetNotVisibleError(
                f"{null_votes}/{total} providers reported target not visible "
                f"({errored} errored)"
            )

        raise RuntimeError(f"All {total} grounding providers exhausted") from last_err

    def _verify_candidates(
        self,
        image: Image,
        candidates: list[BBox],
        target_description: str,
        depth: int,
    ) -> BBox | None:
        W, H = image.size
        half = VERIFY_CROP_SIZE // 2
        for candidate in candidates:
            cx, cy = candidate.center
            x0 = max(0, min(cx - half, W - VERIFY_CROP_SIZE))
            y0 = max(0, min(cy - half, H - VERIFY_CROP_SIZE))
            x1 = min(W, x0 + VERIFY_CROP_SIZE)
            y1 = min(H, y0 + VERIFY_CROP_SIZE)
            crop = image.crop((x0, y0, x1, y1))
            try:
                self.ground(crop, target_description, _depth=depth + 1)
            except TargetNotVisibleError as e:
                logger.error(f"Candidate Verifier Failed: {e}")
                continue
            return candidate
        return None
