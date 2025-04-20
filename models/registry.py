from typing import Callable, Dict
from PIL import Image

MODELS: Dict[str, Callable[[Image.Image], str]] = {}


def register_model(name: str):
    def decorator(fn: Callable[[Image.Image], str]):
        MODELS[name] = fn
        return fn

    return decorator
