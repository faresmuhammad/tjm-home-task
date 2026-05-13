

from src.grounder.prompts import plan_regions_prompt
from src.grounder.providers.base import ModelClient, ModelRequest
from src.grounder.roles import Role, CandidateRegion, PlannerOutput, _denorm_bbox
from PIL.Image import Image

class Planner(Role):
    def __init__(self,clients: ModelClient | list[ModelClient])
        super().__init__(clients)


    def plan(self,image:Image,target_description:str):
        prompt = plan_regions_prompt(target_description)
        for i, client in enumerate(self._clients):

            response = client.execute(ModelRequest(prompt, image))
            data = response.parsed_json or {}
            raw_regions = data.get("regions", [])
            if not raw_regions:
                return PlannerOutput(regions=[], reason=data.get("reason", "no regions returned"))

            regions: list[CandidateRegion] = []
            for r in raw_regions:
                bbox_raw = r.get("bbox")
                if not bbox_raw:
                    continue
                try:
                    bbox = _denorm_bbox(bbox_raw, image.size)
                except (ValueError, TypeError):
                    print("Planner returned invalid bbox: %s", bbox_raw)
                    continue
                regions.append(
                    CandidateRegion(
                        description=r.get("description", "(no description)"),
                        bbox=bbox,
                        neighbors=r.get("neighbors", []),
                    )
                )

            return PlannerOutput(regions=regions)
