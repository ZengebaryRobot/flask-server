from .registry import register_model, configure_camera
import cv2 as cv
import numpy as np
from PIL import Image
from logger import logger

PLACES = [(100, 215, 100, 100), (250, 215, 100, 100), (400, 215, 100, 100)]


def get_limits(color_dict):
    limits = {}
    for color_name, bgr_value in color_dict.items():
        c = np.uint8([[bgr_value]])
        hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)

        lower_limit = hsvC[0][0][0] - 10, 100, 100
        upper_limit = hsvC[0][0][0] + 10, 255, 255

        lower_limit = np.array(lower_limit, dtype=np.uint8)
        upper_limit = np.array(upper_limit, dtype=np.uint8)

        limits[color_name] = (lower_limit, upper_limit)
    return limits


def is_inside(x, y, w, h):
    for idx, (px, py, pw, ph) in enumerate(PLACES):
        if px < x < px + pw and py < y < py + ph:
            return idx
    return -1


colors = {
    "red": [65, 60, 160],
    "white": [255, 255, 255],
    "blue": [230, 216, 173],
    "green": [80, 210, 90],
    "yellow": [65, 210, 200],
    "orange": [80, 140, 235],
}


@configure_camera()
def rubik_camera_config(current_config):
    current_config["brightness"] = 50

    return current_config


@register_model("cups")
def process_image(pil_img: Image.Image) -> str:
    frame = cv.cvtColor(np.array(pil_img), cv.COLOR_RGB2BGR)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    limits = get_limits(colors)

    detected = [None] * len(PLACES)
    max_area = [0] * len(PLACES)

    for color_name, (lower, upper) in limits.items():
        mask = cv.inRange(hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area < 1000:
                continue
            x, y, w, h = cv.boundingRect(cnt)
            ar = w / float(h)
            place_idx = is_inside(x, y, w, h)
            if place_idx == -1 or not (0.5 < ar < 2.0):
                continue

            if area > max_area[place_idx]:
                max_area[place_idx] = int(area)
                detected[place_idx] = color_name

    result = [color for color in detected if color is not None]

    result = ",".join(result) if result else "-1"

    logger.info(f"Result: {result}")

    return result
