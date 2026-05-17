from dataclasses import dataclass
from PIL.Image import Image
from src.grounder.roles import GroundResult
from src.grounder.roles.grounder import Grounder
from src.grounder.roles.planner import Planner
from src.grounder.roles.verifier import Verifier
from src.grounder.strategies.base import GroundingStrategy
from src.grounder.types import Viewport


@dataclass
class _SearchContext:
    target_description:str
    max_depth:int
    min_size_px:int
    sigma:float

@dataclass
class ScreenSeekerConfiguration:
    max_depth:int = 3
    min_size_px:int = 1280
    centrality_sigma:float = 0.3

class ScreenSeekeR(GroundingStrategy):
    def __init__(self, planner: Planner, grounder: Grounder, verifier:Verifier,conf:ScreenSeekerConfiguration = ScreenSeekerConfiguration()) -> None:
        super().__init__()
        self._planner = planner
        self._grounder = grounder
        self._verifier = verifier
        self._conf = conf

    def ground(self, image: Image, target_description: str) -> GroundResult:
        context = _SearchContext(
            target_description=target_description,
            max_depth=self._conf.max_depth,
            min_size_px=self._conf.min_size_px,
            sigma=self._conf.centrality_sigma
        )

        viewport = Viewport.full(*image.size)

        try:
            return self._search(image,viewport,context,depth=0)
        except:


    def _search(self,sub_image:Image,viewport:Viewport,context:_SearchContext,depth:int)->GroundResult:
        is_small_enough = (max(sub_image.size) <= context.min_size_px or depth >= context.max_depth)
        if is_small_enough:
            grounding_output = self._grounder.ground(sub_image,context.target_description)
            screen_bbox = viewport.to_screen(grounding_output.bbox)
            return GroundResult(screen_bbox)




# def filter_overlapping(sorted_candidates,threshold):
    # non-overlapped-candidates = []
    # for each candidate:
        # if iou(another_candidate) > threshold:
            # pass
        # else:
            # non-overlapped-candidates.append(candidate)

# def search(region_crop_image,viewport,context,depth):
    # if region_crop_image.size <= small_size_threshold:
        # grounding-result = grounder.ground(small_size_threshold,target)
        # verification = verifier.verify(grounding-result)
        # if verification.msg == 'found':
            # result = toScreen(grounding-result)
            # return result
        # else:
            # go for another candidate
    # else:
        ## region-candidates = planner.plan(image,target).regions
        #
        # for region in regions:
            # region_crop_img = image.crop(region.bbox)
            # intial-ground = grounder.ground(region_crop_img,target)
            # voting_boxes += inital-ground.boxes + its candidate
        # for vbox in voting_boxes:
            # if vbox.size is tiny:
                # dialted_boxes += dilate_box(vbox)
        # for each vbox, candidate pair:
            # normalize vbox into candidate
            # vote = apply centrality scoring equation
            # candidate_votes += vote
        # sort candidates by score desc
        # filtered_ranked_candidates = filter_overlapping(sorted_candidates)
        # for region in ranked regions: 
            # result = search(region_crop_image,viewport,context,depth + 1)
