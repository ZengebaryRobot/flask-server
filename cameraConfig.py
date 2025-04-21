from requests import get
from logger import logger

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


def send_camera_config(ip, config):
    global CAMERA_CONFIG

    validConfig = {key: value for key, value in config.items() if key in CAMERA_CONFIG}

    if len(validConfig) == 0:
        return True

    try:
        logger.info(f"Sending camera configuration to {ip}")

        response = get(
            ip
            + "/config?"
            + "&".join(f"{key}={value}" for key, value in config.items()),
        )
        response.raise_for_status()

        for key, value in validConfig.items():
            if key in CAMERA_CONFIG and CAMERA_CONFIG[key] != value:
                logger.info(f"Camera configuration updated: {key} = {value}")
                CAMERA_CONFIG[key] = value

        return True
    except Exception as e:
        logger.error(f"Failed to send camera configuration")
        return False
