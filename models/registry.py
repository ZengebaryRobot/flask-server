from typing import Callable, Dict, Optional, Any
from PIL import Image
import requests
import logging

MODELS: Dict[str, Callable[[Image.Image], str]] = {}

CAMERA_CONFIG = {
    "framesize": "QVGA",
    "quality": 10,
    "contrast": 0,
    "brightness": 0,
    "saturation": 0,
    "gainceiling": 0,
    "colorbar": False,
    "awb": True,
    "agc": True,
    "aec": True,
    "hmirror": False,
    "vflip": False,
    "awb_gain": 0,
    "agc_gain": 0,
    "aec_value": 0,
    "aec2": 0,
    "dcw": True,
    "bpc": True,
    "wpc": True,
    "raw_gma": False,
    "lenc": False,
    "special_effect": "none",
    "wb_mode": "auto",
    "ae_level": 0,
    "led_intensity": 0,
}

DID_CAMERA_CONFIG_UPDATE = False


def configure_camera():
    def decorator(fn):
        global DID_CAMERA_CONFIG_UPDATE

        config_updates = fn(dict(CAMERA_CONFIG))

        if not isinstance(config_updates, dict):
            raise TypeError("Camera configuration function must return a dictionary")

        invalid_keys = [key for key in config_updates if key not in CAMERA_CONFIG]
        if invalid_keys:
            raise ValueError(
                f"Invalid camera configuration keys: {invalid_keys}. "
                f"Allowed keys are: {list(CAMERA_CONFIG.keys())}"
            )

        DID_CAMERA_CONFIG_UPDATE = any(
            CAMERA_CONFIG.get(key) != value for key, value in config_updates.items()
        )

        CAMERA_CONFIG.update(config_updates)

        return fn

    return decorator


def register_model(name: str):
    def decorator(fn: Callable[[Image.Image], str]):
        MODELS[name] = fn
        return fn

    return decorator


def get_model_handler(name: str) -> Optional[Callable[[Image.Image], str]]:
    if name not in MODELS:
        return None
    return MODELS[name]


def get_camera_config() -> Dict[str, Any]:
    return CAMERA_CONFIG


def send_camera_config():
    global DID_CAMERA_CONFIG_UPDATE

    if not DID_CAMERA_CONFIG_UPDATE:
        return True

    try:
        response = requests.get(
            "http://192.168.1.18/config?"
            + "&".join(f"{key}={value}" for key, value in CAMERA_CONFIG.items()),
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Failed to send camera configuration")
        return False


def prepare_and_get_model_handler(name: str) -> Optional[Callable[[Image.Image], str]]:
    send_camera_config()

    return get_model_handler(name)
