import cv2 as cv 
from flask import Flask, request
from PIL import Image
import io
from models import MODELS
from logger import logger
from models.registry import get_model_handler
from models.cups import cups_ai
import threading
import logging
from globals import url

logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)


#  how to connect with mobile  
# 1. install ip webcam on mobile 
# 2. open hotspot from your laptop and connect to your mobile 
# 3. start server on laptop flask run or python app.py
# 4. update the url in globals.py with the ip address of your mobile
# 5. open the app and start server on mobile


@app.route("/cups/start", methods=["POST"])
def start_cups():
    num_colors = int(request.args.get("num_colors", default=1))
    print(f"Received num_colors: {num_colors}")
    threading.Thread(target=cups_ai, args=(num_colors,)).start()
    return "Cups AI is running", 200



@app.route("/process", methods=["POST"])
def process_image():
    client_ip = request.remote_addr
    logger.info(f"Request from IP: {client_ip}")

    action_name = request.args.get("action")

    if not action_name:
        logger.error("No action specified in request.")
        return "error", 400

    if action_name not in MODELS:
        logger.error(f"Invalid action specified: '{action_name}'")
        return "error", 400

    logger.info(f"Received request for action: '{action_name}'")

    handler = get_model_handler(action_name)
    if handler is None:
        logger.error(f"No model found for action: '{action_name}'")
        return "error", 400

    try:
        cap = cv.VideoCapture(url)
        ret, img = cap.read()
        if not ret:
            logger.error("Failed to capture frame from video source.")
            return "error", 400
        cap.release()
        logger.info("Image successfully captured from video source.")
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        return "error", 400

    try:
        result = handler(img)
        logger.info(f"Successfully processed image with action: '{action_name}'")
    except Exception as e:
        logger.error(f"Failed to process image with action '{action_name}': {e}")
        return f"error", 500

    return result, 200


if __name__ == "__main__":
    print("Starting Flask server...", flush=True)
    # change port to 8080
    app.run(host="0.0.0.0", port=8080, debug=False)
