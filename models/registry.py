from typing import Callable, Dict, Optional, Any
from PIL import Image
import requests
import logging

MODELS: Dict[str, Callable[[Image.Image], str]] = {}


def register_model(name: str):
    def decorator(fn: Callable[[Image.Image], str]):
        MODELS[name] = fn
        return fn

    return decorator


def get_model_handler(name: str) -> Optional[Callable[[Image.Image], str]]:
    if name not in MODELS:
        return None
    return MODELS[name]


def prepare_and_get_model_handler(name: str) -> Optional[Callable[[Image.Image], str]]:
    send_camera_config()

    return get_model_handler(name)
