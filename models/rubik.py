import logging
import os
import warnings

import torch
from ultralytics import YOLO
from .registry import register_model
from PIL import Image
import cv2
import numpy as np
import models_files.rubik.solver as solver
from models_files.rubik.scan_handling import CubeState

from logger import logger


# Constants
GRID_SIZE = 250
CELL_COUNT = 3
CELL_SIZE = GRID_SIZE // CELL_COUNT

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


logging.getLogger("ultralytics").setLevel(logging.ERROR)


device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
model = YOLO("../models_files/rubik.pt", verbose=False)
model.model.to(device_str)


CONF_THRESH = 0.25
conf = 0.25

color_mapping = {
    "red":    (0,   0, 255),
    "blue":   (255, 0,   0),
    "green":  (0, 255,   0),
    "orange": (0, 165, 255),
    "yellow": (0, 255, 255),
    "white":  (255,255,255),
    "black":  (0,   0,   0),
}

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def rectify_face(detections):
    pts = np.array([[x, y] for (x, y, _) in detections], dtype="float32")
    rect = cv2.minAreaRect(pts)
    box = cv2.boxPoints(rect).astype("float32")
    ordered_box = order_points(box)
    S = int(max(rect[1]))
    dst = np.array([[0, 0], [S - 1, 0], [S - 1, S - 1], [0, S - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(ordered_box, dst)
    return M, S

def assign_to_grid(detections, M, S):
    # build empty 3×3 grid
    grid = [[None]*3 for _ in range(3)]
    for x, y, label in detections:
        if label == "Face":
            continue
        pt = np.array([[[x, y]]], dtype="float32")
        trans = cv2.perspectiveTransform(pt, M)[0][0]
        col = min(2, int(trans[0] / (S/3)))
        row = min(2, int(trans[1] / (S/3)))
        if grid[row][col] is None:
            grid[row][col] = label

    # flatten row-major, fill missing with "black"
    result = []
    for r in range(3):
        for c in range(3):
            result.append(grid[r][c] or "black")
    return result

def process_frame(pil_img: Image.Image) -> list[str]:
    """
    Given a Pillow image and a loaded YOLO model, returns a list of 9
    color-label strings for the cube face (row-major), defaulting to
    'black' if a cell isn't detected or if there are <4 detections.
    """
    # 1) convert PIL→OpenCV BGR
    rgb = np.array(pil_img)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    # 2) run detection
    results = model.predict(bgr, conf=conf, verbose=False)
    if not results or len(results[0].boxes) == 0:
        return ["black"] * 9

    # 3) extract center points + labels
    dets = []
    names = results[0].names
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        cx = float((x1 + x2) / 2)
        cy = float((y1 + y2) / 2)
        lbl = names[int(box.cls)]
        dets.append((cx, cy, lbl))

    # 4) if enough for a perspective transform, compute grid
    if len(dets) >= 4:
        M, S = rectify_face(dets)
        return assign_to_grid(dets, M, S)

    # 5) otherwise all black
    return ["black"] * 9
    
movements_map = {
    'U': 1,
    'F': 3,
    'D': 4,
    'R': 2,
    'L': 5
}

scans = []
@register_model("rubik")
def main(img: Image.Image) -> str:
    # Save the input image exactly as received
    # fileName = "Scan-" + str(len(scans)) + ".png"
    # img.save(fileName)
    
    
    # Process frame
    colors = process_frame(img)
    colors = [color[0] for color in colors]
    logger.info("Image processing completed")
    
    if colors:
        # Process detected colors
        scan = ""

        for i in range(CELL_COUNT):
            row = "".join(colors[i*CELL_COUNT:(i+1)*CELL_COUNT])
            # logger.info(f"row: {row}")
            scan += row
        scans.append([scan])
        logger.info("Scan " + str(len(scans)) +"completed: " + scan)

                    
    # Process and solve cube
    if len(scans) == 11:
        cube = CubeState(scans)
        cube.process_scans()
        cubestring = cube.get_cube_state()
        print(cubestring)
        color_map = {
            'B': 'W',
            'F': 'Y',
            'R': 'G',
            'L': 'B',
            'D': 'R',
            'U': 'O'
        }
        final_string = "".join([color_map[c] for c in cubestring])
        print(final_string)
        sol = solver.solve(cubestring, 20, 5)
        if sol.startswith("Error"):
            raise ValueError("Error in solving the cube: " + sol)
        
        moves = sol.split(" ")
        moves = moves[:-1]  # remove the last item
        sol = ','.join([str(movements_map[move[0]]) + move[1] for move in moves])
        
        logger.info("Result: " + sol)
        return sol
    else:
        return "".join(scan)
    
@register_model("rubikReset")
def reset_rubik(img: Image.Image) -> str:
    global scans
    scans = []
    logger.info("Rubik's cube reset")
    return "1"