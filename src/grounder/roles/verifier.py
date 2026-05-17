
from dataclasses import dataclass

from PIL.Image import Image
from src.grounder.prompts import verify_prompt
from src.grounder.providers.base import ModelClient, ModelRequest
from src.grounder.roles import Role
from src.log import logger


@dataclass
class VerificationOutout:
    verdict:str

    @property
    def verified(self)->bool:
        return self.verdict == "is_target"
        

class Verifier(Role):
    def __init__(self,clients: ModelClient | list[ModelClient])
        super().__init__(clients)

    def verify(self,image:Image,target_description:str) -> VerificationOutout:
        prompt = verify_prompt(target_description)

        for i, client in enumerate(self._clients):
            try:
                response = client.execute(ModelRequest(prompt,image))
                data = response.parsed_json or {}
                verdict = data.get("verdict")
                if verdict not in {"is_target","not_found"}:
                    logger.warning(f"Unknown verdict '{verdict}', treating as not_found")
                    verdict = "not_found"
                
                return VerificationOutout(verdict)    
            except:
                logger.error(f"Verification Failed: client {i+1}/{len(clients)}")

        return VerificationOutout("not_found")