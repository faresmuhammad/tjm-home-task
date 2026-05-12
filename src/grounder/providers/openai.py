import json

from src.grounder.providers._common import encode_image_b64, extract_json
from src.grounder.providers.base import ModelClient, ModelRequest, ModelResponse


class OpenAIClient(ModelClient):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise Exception("OpenAI: api key is required")
        self._api_key = api_key
        self._model = model
        self._client = None

    def instantiate_client(self):
        if self._client is not None:
            return

        try:
            from openai import OpenAI
        except ImportError:
            raise Exception("OpenAI sdk is not installed")

        self._client = OpenAI(api_key=self._api_key)

    def send_api(self, request: ModelRequest) -> ModelResponse:

        b64 = encode_image_b64(request.image, format="PNG")

        response = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": request.prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{b64}",
                        },
                    ],
                }
            ],
        )

        text = response.output_text
        parsed_json = extract_json(text)
        return ModelResponse(text=text, parsed_json=parsed_json)
