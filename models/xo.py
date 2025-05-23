from .registry import register_model
from PIL import Image
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import warnings
import os
import logging
from logger import logger

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

cv2.setLogLevel(0)

logging.getLogger("ultralytics").setLevel(logging.ERROR)


device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, "models_files", "xo.pt")

# Add debug information to help diagnose
print(f"Looking for model at: {model_path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory exists: {os.path.exists(os.path.dirname(model_path))}")

# Then load the model with the absolute path
model = YOLO(model_path, verbose=False)
model.model.to(device_str)
print("Model loaded successfully XO.")


def process_pieces(frame):
    results = model.predict(frame, conf=0.25)
    detections = []
    if results and len(results[0].boxes) > 0:
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            label = results[0].names[int(box.cls)]
            if label in ["X", "O"]:
                detections.append((x1, y1, x2, y2, label))
    return detections


def convert_grid_to_cells(grid):
    deduplicated_grid = []
    seen_positions = set()
    for x, y, label in grid:
        pos = (
            round(x / 5) * 5,
            round(y / 5) * 5,
        )
        if pos not in seen_positions:
            seen_positions.add(pos)
            deduplicated_grid.append((x, y, label))
        else:
            for i, (existing_x, existing_y, existing_label) in enumerate(
                deduplicated_grid
            ):
                existing_pos = (round(existing_x / 5) * 5, round(existing_y / 5) * 5)
                if existing_pos == pos:
                    if existing_label == "-" and label in ["X", "O"]:
                        deduplicated_grid[i] = (x, y, label)
                    break

    sorted_grid = sorted(deduplicated_grid, key=lambda x: (x[1], x[0]))

    rows = []
    current_row = []
    last_y = None
    y_threshold = 10

    for x, y, label in sorted_grid:
        if last_y is None or abs(y - last_y) <= y_threshold:
            current_row.append((x, y, label))
        else:
            current_row.sort(key=lambda x: x[0])
            row = [item[2] for item in current_row]
            row.extend(["-"] * (5 - len(row)))
            rows.append(row[:5])
            current_row = [(x, y, label)]
        last_y = y

    if current_row:
        current_row.sort(key=lambda x: x[0])
        row = [item[2] for item in current_row]
        row.extend(["-"] * (5 - len(row)))
        rows.append(row[:5])

    cells = rows
    while len(cells) < 3:
        cells.append(["-"] * 5)
    if len(cells) > 3:
        cells = cells[:3]

    return cells


def detect_tic_tac_toe(frame):
    # Resize for faster processing
    cv_img = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    frame = cv2.resize(cv_img, (320, 240))

    # Crop frame to focus on the game area
    x1, y1 = 48, 64
    x2, y2 = 294, 209
    frame_original = frame.copy()
    frame = frame[y1:y2, x1:x2]

    # Draw crop boundaries on original frame for visualization
    cv2.rectangle(frame_original, (x1, y1), (x2, y2), (255, 255, 0), 2)

    # Detect pieces with YOLO
    detections = process_pieces(frame)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Apply Otsu's thresholding with bias
    otsu_threshold, _ = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    bias = 28
    biased_threshold = min(255, otsu_threshold + bias)
    _, thresh = cv2.threshold(blurred, biased_threshold, 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.bitwise_not(thresh)

    # Apply brightness mask
    bright_mask = gray > 110
    thresh = cv2.bitwise_and(thresh, thresh, mask=bright_mask.astype(np.uint8) * 255)

    # Morphological operations
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Collect grid points
    grid = []
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 0.8 <= aspect_ratio <= 1.2 and 12 < w < 65:
                roi = gray[y : y + h, x : x + w]
                avg_brightness = np.mean(roi)
                if avg_brightness > 100:
                    center_x = int(x + w / 2)
                    center_y = int(y + w / 2)
                    grid.append((center_x, center_y, "-"))

    # Add detected pieces to grid
    for x1, y1, x2, y2, label in detections:
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        grid.append((center_x, center_y, label))

    # Convert grid to cells
    cells = convert_grid_to_cells(grid)
    return cells


@register_model("xo")
def process_image(img: Image.Image) -> str:
    result = np.array(detect_tic_tac_toe(img)).flatten().tolist()

    m = {"X": 1, "O": 2, "-": 0}

    result = ",".join([str(m[item]) for item in result])

    logger.info(f"Result: {result}")

    return result
