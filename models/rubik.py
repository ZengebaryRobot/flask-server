from .registry import register_model, configure_camera
import cv2 as cv
import numpy as np
from PIL import Image
from logger import logger

GRID_SIZE = 300
CELL_COUNT = 3
CELL_SIZE = GRID_SIZE // CELL_COUNT


def get_limits(color_dict):
    limits = {}
    for color_name, bgr_value in color_dict.items():
        if color_name == "white":
            lower_limit = np.array([0, 0, 150])
            upper_limit = np.array([255, 60, 255])
        elif color_name == "dark_red":
            lower_limit = np.array([0, 100, 50], dtype=np.uint8)
            upper_limit = np.array([10, 255, 255], dtype=np.uint8)
        else:
            c = np.uint8([[bgr_value]])
            hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)
            h = hsvC[0][0][0]
            lower_limit = np.array((h - 10, 100, 100), dtype=np.uint8)
            upper_limit = np.array((h + 10, 255, 255), dtype=np.uint8)
        limits[color_name] = (lower_limit, upper_limit)
    return limits


colors = {
    "red": [65, 60, 160],
    "white": [255, 255, 255],
    "blue": [230, 216, 173],
    "green": [80, 210, 90],
    "yellow": [65, 210, 200],
    "orange": [80, 140, 235],
}


def draw_grid(frame):
    for x in range(0, GRID_SIZE, CELL_SIZE):
        cv.line(frame, (x, 0), (x, GRID_SIZE), (255, 255, 255), 2)
    for y in range(0, GRID_SIZE, CELL_SIZE):
        cv.line(frame, (0, y), (GRID_SIZE, y), (255, 255, 255), 2)
    return frame


def get_cell_colors(frame):

    cell_colors = []
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    limits = get_limits(colors)

    for row in range(CELL_COUNT):
        for col in range(CELL_COUNT):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            cell = hsv_frame[y : y + CELL_SIZE, x : x + CELL_SIZE]

            detected_color = None
            max_pixels = 0
            for color_name, (lower, upper) in limits.items():
                mask = cv.inRange(cell, lower, upper)
                pixel_count = cv.countNonZero(mask)
                if pixel_count > max_pixels:
                    max_pixels = pixel_count
                    detected_color = color_name

            cell_colors.append(detected_color)
    return cell_colors


@configure_camera()
def rubik_camera_config(current_config):
    current_config["brightness"] = 50

    return current_config


@register_model("rubik")
def process_image(pil_img: Image.Image) -> str:
    cv_frame = cv.cvtColor(np.array(pil_img), cv.COLOR_RGB2BGR)

    h, w = cv_frame.shape[:2]
    if h < GRID_SIZE or w < GRID_SIZE:
        raise ValueError(f"Image must be at least {GRID_SIZE}×{GRID_SIZE}, got {w}×{h}")

    start_x = (w - GRID_SIZE) // 2
    start_y = (h - GRID_SIZE) // 2
    square = cv_frame[start_y : start_y + GRID_SIZE, start_x : start_x + GRID_SIZE]

    flat_colors = get_cell_colors(square)

    m = {
        None: 0,
        "red": 1,
        "white": 2,
        "blue": 3,
        "green": 4,
        "yellow": 5,
        "orange": 6,
    }

    result = ",".join([str(m[color]) for color in flat_colors])

    logger.info(f"Result: {result}")

    return result
