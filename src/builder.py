from typing import Optional

from dotenv.main import os

from src.grounder.providers.base import ModelClient
from src.grounder.providers.openai import OpenAIClient
from src.grounder.providers.openrouter import OpenRouterClient
from src.grounder.roles.grounder import Grounder
from src.grounder.strategies.base import GroundingStrategy
from src.grounder.strategies.direct import DirectStrategy
from src.grounder.strategies.reground import RegroundStrategy


def build_client(provider: str, model: Optional[str] = None) -> ModelClient:
    if provider == "openrouter":
        __model = model or "qwen/qwen3-vl-32b-instruct"
        return OpenRouterClient(os.getenv("OPENROUTER_API_KEY", ""), __model)
    elif provider == "openai":
        __model = model or "gpt-4o"
        return OpenAIClient(os.getenv("OPENAI_API_KEY", ""), __model)

    else:
        raise Exception("Provider not supported")


def build_clients(specs: list[tuple[str, Optional[str]]]) -> list[ModelClient]:
    return [build_client(provider, model) for provider, model in specs]


def build_strategy(name: str, grounder: Grounder) -> GroundingStrategy:
    name = name.lower()
    if name == "direct":
        return DirectStrategy(grounder)
    elif name == "reground":
        return RegroundStrategy(grounder)
    else:
        raise Exception(f"Strategy Not supported: {name}")
