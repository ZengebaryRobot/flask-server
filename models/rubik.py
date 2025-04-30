from .registry import register_model
from PIL import Image
import cv2 as cv
import numpy as np
import models_files.rubik.solver as solver
from models_files.rubik.scan_handling import CubeState

from logger import logger


# Constants
GRID_SIZE = 300
CELL_COUNT = 3
CELL_SIZE = GRID_SIZE // CELL_COUNT

# Color definitions (BGR format)
COLORS = {
    'R': [65, 60, 160],    # Red
    'W': [255, 255, 255],  # White
    'B': [230, 216, 173],  # Blue
    'G': [80, 210, 90],    # Green
    'Y': [65, 210, 200],   # Yellow
    'O': [80, 140, 235]    # Orange
}

def get_color_limits(color_dict):
    """Generate HSV color limits for detection"""
    limits = {}
    for color_name, bgr_value in color_dict.items():
        if color_name == 'W':  # Special case for white
            lower_limit = np.array([0, 0, 150])
            upper_limit = np.array([255, 60, 255])
        elif color_name == 'R':  # Special case for red
            lower_limit = np.array([0, 100, 50], dtype=np.uint8)
            upper_limit = np.array([10, 255, 255], dtype=np.uint8)
        else:
            c = np.uint8([[bgr_value]])
            hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)
            hue = hsvC[0][0][0]
            lower_limit = np.array([hue - 10, 100, 100], dtype=np.uint8)
            upper_limit = np.array([hue + 10, 255, 255], dtype=np.uint8)
        
        limits[color_name] = (lower_limit, upper_limit)
    return limits

def draw_grid(frame):
    """Draw 3x3 grid on the frame"""
    for i in range(0, GRID_SIZE, CELL_SIZE):
        cv.line(frame, (i, 0), (i, GRID_SIZE), (255, 255, 255), 2)
        cv.line(frame, (0, i), (GRID_SIZE, i), (255, 255, 255), 2)
    return frame

def get_cell_colors(frame, color_limits):
    """Detect colors in each cell of the 3x3 grid"""
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    cell_colors = []
    
    for row in range(CELL_COUNT):
        for col in range(CELL_COUNT):
            x, y = col * CELL_SIZE, row * CELL_SIZE
            cell = hsv_frame[y:y+CELL_SIZE, x:x+CELL_SIZE]
            
            detected_color, max_pixels = None, 0
            for color_name, (lower, upper) in color_limits.items():
                mask = cv.inRange(cell, lower, upper)
                pixel_count = cv.countNonZero(mask)
                if pixel_count > max_pixels:
                    max_pixels = pixel_count
                    detected_color = color_name
            
            cell_colors.append(detected_color)
    return cell_colors

def process_frame(frame, color_limits):
    """Process video frame and handle scanning when 's' is pressed"""
    height, width = frame.shape[:2]
    start_x = (width - GRID_SIZE) // 2
    start_y = (height - GRID_SIZE) // 2
    square_frame = frame[start_y:start_y+GRID_SIZE, start_x:start_x+GRID_SIZE]
    
    if square_frame.shape[:2] != (GRID_SIZE, GRID_SIZE):
        return None, frame
    
    # Draw alignment rectangle
    cv.rectangle(frame, (start_x, start_y), 
                (start_x+GRID_SIZE, start_y+GRID_SIZE), (0, 255, 0), 2)
    
    # Prepare grid view
    grid_frame = draw_grid(square_frame.copy())
    

    return get_cell_colors(square_frame, color_limits)

movements_map = {
    'U': 1,
    'F': 2,
    'D': 3,
    'R': 4,
    'L': 5
}

scans = []
@register_model("rubik")
def main(img: Image.Image) -> str:
    # Initialize components
    # Get keyboard input
        
    # Process frame with keyboard input
    
    color_limits = get_color_limits(COLORS)
    colors = process_frame(np.array(img), color_limits)
    
    
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
        
        sol = solver.solve(cubestring, 20, 2)
        if sol.startswith("Error"):
            raise ValueError("Error in solving the cube: " + sol)
        
        moves = sol.split(" ")
        moves = moves[:-1]  # remove the last item
        sol = ','.join([str(movements_map[move[0]]) + move[1] for move in moves])
        
        logger.info("Result: " + sol)
        return sol
    else:
        return "-1"