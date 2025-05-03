import cv2 as cv
import numpy as np
import time
from threading import Lock
from .registry import register_model
from PIL import Image
from logger import logger

from globals import url

PLACES = [(120, 160, 75, 80), (260, 165, 75, 80), (400, 170, 75, 80)]
lock = Lock()

# STREAM_URL = "http://192.168.66.137/stream"

STREAM_URL = url

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
    for index, point in enumerate(PLACES):
        if (
            point[0] < x < point[0] + point[2]
            and point[1] < y < point[1] + point[3]
            and w < point[2]
            and h < point[3]
        ):
            return index
    return -1


def is_most_inside(x, y, w, h):
    for index, point in enumerate(PLACES):
        place_x_range = (point[0], point[0] + point[2])
        bbox_x_range = (x, x + w)
        place_y_range = (point[1], point[1] + point[3])
        bbox_y_range = (y, y + h)
        x_overlap_min = max(place_x_range[0], bbox_x_range[0])
        x_overlap_max = min(place_x_range[1], bbox_x_range[1])
        y_overlap_min = max(place_y_range[0], bbox_y_range[0])
        y_overlap_max = min(place_y_range[1], bbox_y_range[1])
        overlap_width = max(0, x_overlap_max - x_overlap_min)
        overlap_height = max(0, y_overlap_max - y_overlap_min)
        intersection_area = overlap_width * overlap_height
        box_area = point[2] * point[3]
        if box_area == 0:
            return -1
        overlap_percentage = (intersection_area / box_area) * 100
        if overlap_percentage > 50:
            return index
    return -1


final_result = [None, None, None]


def cups_ai(required_objects=1):
    colors = {
        "red": [65, 60, 160],
        "blue": [230, 216, 173],
        "yellow": [110, 170, 170],
    }
    result = [None, None, None]
    ok = True
    capture = cv.VideoCapture(STREAM_URL)
    limits = get_limits(colors)

    DISAPPEARANCE_THRESHOLD = 1
    STOP_TIME = 5.0
    tracking_mode = False
    bboxes_colors = []
    bboxes_places = []
    bboxes_coords = []

    expected_objects = {}
    disappearance_start_time = None
    # Detection Mode
    while ok and not tracking_mode:
        logger.info("Detection Mode for cups capturing")
        ok, frame = capture.read()
        if not ok:
            break

        for place in PLACES:
            frame = cv.rectangle(
                frame,
                (place[0], place[1]),
                (place[0] + place[2], place[1] + place[3]),
                (0, 0, 0),
                2,
            )

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        current_objects = {}
        num_detected_objects = 0

        for color_name, hsv_value in limits.items():
            mask = cv.inRange(hsv, hsv_value[0], hsv_value[1])
            kernel = np.ones((5, 5), np.uint8)
            mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
            contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv.contourArea(contour)
                x, y, w, h = cv.boundingRect(contour)
                aspect_ratio = w / h
                place = is_inside(x, y, w, h)
                if area > 1000 and 0.5 < aspect_ratio < 2.0 and place != -1:
                    if place not in current_objects or area > cv.contourArea(
                        cv.boxPoints(cv.minAreaRect(contour))
                    ):
                        current_objects[place] = (
                            color_name,
                            (
                                PLACES[place][0],
                                PLACES[place][1],
                                PLACES[place][2],
                                PLACES[place][3],
                            ),
                        )
                        num_detected_objects += 1
                        frame = cv.rectangle(
                            frame,
                            (PLACES[place][0], PLACES[place][1]),
                            (
                                PLACES[place][0] + PLACES[place][2],
                                PLACES[place][1] + PLACES[place][3],
                            ),
                            colors[color_name],
                            2,
                        )

        current_time = time.time()

        if num_detected_objects >= required_objects and not expected_objects:
            expected_objects = current_objects.copy()
            disappearance_start_time = None
        elif expected_objects:
            expected_colors = {color for _, (color, _) in expected_objects.items()}
            detected_colors = {color for _, (color, _) in current_objects.items()}

            any_color_detected = bool(expected_colors & detected_colors)

            if any_color_detected:
                new_expected_objects = {}
                for place_idx, (color_name, bbox) in current_objects.items():
                    if color_name in expected_colors:
                        new_expected_objects[place_idx] = (color_name, bbox)

                for place_idx, (color_name, bbox) in expected_objects.items():
                    if (
                        color_name not in detected_colors
                        and color_name in expected_colors
                    ):
                        new_expected_objects[place_idx] = (color_name, bbox)

                expected_objects = new_expected_objects
                disappearance_start_time = None
            else:
                if disappearance_start_time is None:
                    disappearance_start_time = current_time
                elif current_time - disappearance_start_time >= DISAPPEARANCE_THRESHOLD:
                    for place_idx, (color_name, bbox) in expected_objects.items():
                        bboxes_colors.append(color_name)
                        bboxes_places.append(place_idx)
                        bboxes_coords.append(bbox)
                    tracking_mode = True
        else:
            disappearance_start_time = None
            expected_objects = {}

        cv.imshow("frame", frame)
        if cv.waitKey(1) == ord("d"):
            break

    # Tracking Mode
    if tracking_mode and ok:
        trackers_kcf = []
        trackers_csrt = []
        use_csrt = [False] * len(bboxes_places)
        prev_bboxes = [None] * len(bboxes_places)
        initial_bboxes = []
        csrt_frame_counters = [0] * len(bboxes_places)
        condition_start_time = None

        for bbox in bboxes_coords:
            x, y, w, h = bbox
            initial_bboxes.append((w, h))
            tracker_kcf = cv.TrackerKCF_create()
            tracker_csrt = cv.TrackerCSRT_create()
            tracker_kcf.init(frame, (x, y, w, h))
            tracker_csrt.init(frame, (x, y, w, h))
            trackers_kcf.append(tracker_kcf)
            trackers_csrt.append(tracker_csrt)

        while ok:
            ok, frame = capture.read()
            if not ok:
                break

            valid_trackers_inside = 0

            for i, (tracker_kcf, tracker_csrt) in enumerate(
                zip(trackers_kcf, trackers_csrt)
            ):
                if not use_csrt[i]:
                    success, bbox = tracker_kcf.update(frame)
                else:
                    success, bbox = tracker_csrt.update(frame)

                if success:
                    x, y, w, h = [int(v) for v in bbox]
                    init_w, init_h = initial_bboxes[i]
                    center_x = x + w / 2
                    center_y = y + h / 2
                    x = int(center_x - init_w / 2)
                    y = int(center_y - init_h / 2)
                    w = init_w
                    h = init_h
                    x = max(0, min(x, frame.shape[1] - w))
                    y = max(0, min(y, frame.shape[0] - h))
                    cv.rectangle(
                        frame, (x, y), (x + w, y + h), colors[bboxes_colors[i]], 2
                    )
                    place_index = is_most_inside(x, y, w, h)
                    if place_index != -1:
                        valid_trackers_inside += 1
                        result[place_index] = bboxes_colors[i]
                    else:
                        valid_trackers_inside -= 1

                    if not use_csrt[i]:
                        if prev_bboxes[i] is not None:
                            prev_x, prev_y, _, _ = prev_bboxes[i]
                            bbox_change = np.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                            confidence = 1 / (1 + bbox_change)
                            if confidence < 0.7:
                                use_csrt[i] = True
                                csrt_frame_counters[i] = 0
                        prev_bboxes[i] = (x, y, w, h)
                    else:
                        csrt_frame_counters[i] += 1
                        if csrt_frame_counters[i] >= 10:
                            use_csrt[i] = False
                            tracker_kcf = cv.TrackerKCF_create()
                            tracker_kcf.init(frame, (x, y, w, h))
                            trackers_kcf[i] = tracker_kcf
                else:
                    cv.putText(
                        frame,
                        f"Lost {i+1}",
                        (10, 50 + i * 30),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

            if valid_trackers_inside == required_objects:
                if condition_start_time is None:
                    condition_start_time = time.time()
                elif time.time() - condition_start_time >= STOP_TIME:
                    break
            else:
                condition_start_time = None
                result = [None, None, None]

            for place in PLACES:
                frame = cv.rectangle(
                    frame,
                    (place[0], place[1]),
                    (place[0] + place[2], place[1] + place[3]),
                    (0, 0, 0),
                    2,
                )

            cv.imshow("Multi-Object Tracking", frame)
            if cv.waitKey(1) & 0xFF == ord("d"):
                break
        with lock:
            final_result = result
        capture.release()
        cv.destroyAllWindows()


@register_model("cupsResult")
def cups_result(img: Image.Image) -> str:
    global final_result

    with lock:
        if (
            final_result[0] is not None
            and final_result[1] is not None
            and final_result[2] is not None
        ):
            return ",".join([str(x) for x in final_result])

    return "-1"
