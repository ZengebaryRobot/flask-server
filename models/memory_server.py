from .registry import register_model
from PIL import Image
import cv2
import numpy as np
import os
from ultralytics import YOLO
from logger import logger

# Constants for the grid
ROWS = 2
COLS = 3

def order_points(pts):
    """Order points in top-left, top-right, bottom-right, bottom-left order"""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def create_grid_matrix(points, rows=ROWS, cols=COLS):
    """Create perspective transform matrix for the grid"""
    src_pts = order_points(np.array(points, dtype=np.float32))
    
    width_top = np.linalg.norm(src_pts[1] - src_pts[0])
    width_bottom = np.linalg.norm(src_pts[2] - src_pts[3])
    avg_width = (width_top + width_bottom) / 2
    
    height_left = np.linalg.norm(src_pts[3] - src_pts[0])
    height_right = np.linalg.norm(src_pts[2] - src_pts[1])
    avg_height = (height_left + height_right) / 2
    
    cell_size = min(avg_width / cols, avg_height / rows)
    target_width = cell_size * cols
    target_height = cell_size * rows
    
    vertical_scale = 1.5
    target_height *= vertical_scale
    
    dst_pts = np.array([
        [0, 0],
        [target_width, 0],
        [target_width, target_height],
        [0, target_height]
    ], dtype=np.float32)
    
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    return M, (int(target_width), int(target_height))

def load_grid_coordinates():
    """Load grid coordinates from file"""
    coords_file = 'coords.txt'
    if not os.path.exists(coords_file):
        logger.warning(f"{coords_file} not found")
        return None
    
    points = []
    try:
        with open(coords_file, 'r') as f:
            for line in f:
                x, y = map(int, line.strip().split(','))
                points.append((x, y))
        
        if len(points) != 4:
            logger.warning(f"Expected 4 points in {coords_file}, but found {len(points)}")
            return None
            
        return points
    except Exception as e:
        logger.error(f"Error loading coordinates: {e}")
        return None

@register_model("matrix_cards")
def process_image(pil_img: Image.Image) -> str:
    """Process an image to detect cards in a grid and return a comma-separated string result"""
    # Convert PIL Image to OpenCV format
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Load the model
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "models_files", "yolo11_cards.pt")
    
    logger.info(f"Loading YOLO model from {model_path}")
    try:
        model = YOLO(model_path)
        logger.info("Matrix cards model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading YOLO model: {e}")
        return "error"
    
    # Get grid points - first try from file, then use default
    points = load_grid_coordinates()
    
    # If no points are available, use automatic grid
    if points is None:
        h, w = frame.shape[:2]
        points = [
            (int(w*0.1), int(h*0.1)),   # top-left
            (int(w*0.9), int(h*0.1)),   # top-right
            (int(w*0.9), int(h*0.9)),   # bottom-right
            (int(w*0.1), int(h*0.9))    # bottom-left
        ]
        logger.info("Using automatic grid points")
    else:
        logger.info("Using grid points from coords.txt")
    
    # Create transform matrix
    M, grid_size = create_grid_matrix(points)
    
    # Initialize grid for card detection
    grid_labels = [[None for _ in range(COLS)] for _ in range(ROWS)]
    grid_confidences = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    
    # Run detection
    results = model.predict(
        source=frame,
        conf=0.3,
        imgsz=1600,
        verbose=False
    )
    
    # Process detection results
    for r in results:
        boxes = r.boxes
        for i in range(len(boxes)):
            x1, y1, x2, y2 = map(int, boxes.xyxy[i])
            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            # Transform center point to grid coordinates
            grid_pt = cv2.perspectiveTransform(
                np.array([[center]], dtype=np.float32), M)[0][0]
            
            if 0 <= grid_pt[0] < grid_size[0] and 0 <= grid_pt[1] < grid_size[1]:
                cell_col = int(grid_pt[0] // (grid_size[0] / COLS))
                cell_row = int(grid_pt[1] // (grid_size[1] / ROWS))
                cell_col = min(max(cell_col, 0), COLS - 1)
                cell_row = min(max(cell_row, 0), ROWS - 1)
                
                label = r.names[int(boxes.cls[i])]
                conf = float(boxes.conf[i])
                
                if conf > grid_confidences[cell_row][cell_col]:
                    grid_labels[cell_row][cell_col] = label
                    grid_confidences[cell_row][cell_col] = conf
    
    # Format the results as a comma-separated string
    # Format: row,col,label or Empty if no card detected
    result = []
    for row in range(ROWS):
        for col in range(COLS):
            if grid_labels[row][col] is not None:
                result.append(f"{row},{col},{grid_labels[row][col]}")
            else:
                result.append(f"{row},{col},Empty")
    
    output = ",".join(result)
    logger.info(f"Matrix cards result: {output}")
    
    return output