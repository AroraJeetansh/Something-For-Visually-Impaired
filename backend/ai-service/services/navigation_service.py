from transformers import pipeline
from PIL import Image
import numpy as np
import time

from services.path_planner import plan_path
from services.speech_service import build_navigation_speech
from services.scene_memory import SceneMemory
from services.distance_estimator import classify_distance

# ==========================================================
# LOAD DEPTH MODEL
# ==========================================================

depth_estimator = pipeline(
    task="depth-estimation",
    model="depth-anything/Depth-Anything-V2-Small-hf",
    local_files_only=True
)

# ==========================================================
# CONFIG
# ==========================================================

MAX_DEPTH_SIZE = 640

# ==========================================================
# HELPERS
# ==========================================================

def prepare_depth_image(image):

    original_width, original_height = image.size

    depth_image = image.copy()

    depth_image.thumbnail(
        (MAX_DEPTH_SIZE, MAX_DEPTH_SIZE),
        Image.Resampling.LANCZOS
    )

    scale_x = depth_image.width / original_width
    scale_y = depth_image.height / original_height

    return depth_image, scale_x, scale_y


def get_direction(center_x, image_width):

    ratio = center_x / image_width

    if ratio < 0.20:
        return "far_left"

    elif ratio < 0.40:
        return "left"

    elif ratio < 0.60:
        return "center"

    elif ratio < 0.80:
        return "right"

    return "far_right"

# ==========================================================
# MAIN
# ==========================================================

def analyze_navigation(image, detections, scene_memory: SceneMemory):
    """
    scene_memory: the caller's per-session SceneMemory instance
    (see services/session_memory_store.py). Passing it in here, rather
    than creating one inside this function, is what lets memory persist
    correctly across requests for the same user without leaking into
    other users' sessions.
    """

    print("\nStarting Navigation Analysis...")

    depth_image, scale_x, scale_y = prepare_depth_image(image)

    print(
        "Depth Input Size:",
        depth_image.size
    )

    start = time.time()

    depth_result = depth_estimator(
        depth_image
    )

    print(
        f"Depth Model       : {time.time()-start:.2f}s"
    )

    depth_map = np.array(
        depth_result["depth"]
    )

    depth_height, depth_width = depth_map.shape

    max_depth = float(
        np.max(depth_map)
    )

    image_area = image.width * image.height

    objects = []

    processing_start = time.time()

    for detection in detections:

        name = detection["name"]

        confidence = detection["confidence"]

        x1, y1, x2, y2 = detection["box"]

        x1_d = int(x1 * scale_x)
        x2_d = int(x2 * scale_x)

        y1_d = int(y1 * scale_y)
        y2_d = int(y2 * scale_y)

        x1_d = max(
            0,
            min(x1_d, depth_width - 1)
        )

        x2_d = max(
            0,
            min(x2_d, depth_width)
        )

        y1_d = max(
            0,
            min(y1_d, depth_height - 1)
        )

        y2_d = max(
            0,
            min(y2_d, depth_height)
        )

        region = depth_map[
            y1_d:y2_d,
            x1_d:x2_d
        ]

        if region.size == 0:
            continue

        median_depth = float(
            np.median(region)
        )

        closeness = 1 - (
            median_depth / max_depth
        )

        closeness = max(
            0,
            min(closeness, 1)
        )

        box_width = x2 - x1

        box_height = y2 - y1

        box_area = box_width * box_height

        normalized_area = (
            box_area / image_area
        )

        center_x = (x1 + x2) / 2

        direction = get_direction(
            center_x,
            image.width
        )

        objects.append({

            "object": name,

            "confidence": round(
                confidence,
                2
            ),

            "direction": direction,

            "depth": round(
                median_depth,
                2
            ),

            "closeness": round(
                closeness,
                3
            ),

            "normalized_area": round(
                normalized_area,
                4
            ),

            "box": [
                x1,
                y1,
                x2,
                y2
            ]

        })

    # ---------------------------------------
    # Processing Time
    # ---------------------------------------

    print(
        f"Object Processing : {time.time()-processing_start:.2f}s"
    )

    # ---------------------------------------
    # Distance Classification
    # ---------------------------------------

    distance_start = time.time()

    objects = classify_distance(
        objects,
        depth_map
    )

    print(
        f"Distance Labels   : {time.time()-distance_start:.2f}s"
    )

    # ---------------------------------------
    # Sort Objects
    # ---------------------------------------

    sort_start = time.time()

    objects.sort(

        key=lambda x: (
            x["closeness"],
            x["normalized_area"]
        ),

        reverse=True

    )

    objects = objects[:3]

    print(
        f"Sorting           : {time.time()-sort_start:.2f}s"
    )

    # ---------------------------------------
    # Path Planner
    # ---------------------------------------

    planner_start = time.time()

    path = plan_path(
        objects
    )

    print(
        f"Path Planner      : {time.time()-planner_start:.2f}s"
    )

    # ---------------------------------------
    # Scene Memory
    # ---------------------------------------

    memory_start = time.time()

    annotated_objects, path_just_cleared = scene_memory.update(
        objects,
        path
    )

    print(
        f"Scene Memory      : {time.time()-memory_start:.2f}s"
    )

    # ---------------------------------------
    # Speech
    # ---------------------------------------

    speech_start = time.time()

    speech = build_navigation_speech(

        objects,

        path,

        annotated_objects=annotated_objects,

        path_just_cleared=path_just_cleared

    )

    print(
        f"Speech            : {time.time()-speech_start:.2f}s"
    )

    print(
        f"Navigation Total  : {time.time()-start:.2f}s"
    )

    # ---------------------------------------
    # Debug
    # ---------------------------------------

    print("\nNavigation Summary")
    print("=" * 50)

    for obj in annotated_objects:

        print(

            f"{obj['object']:15}"

            f"{obj['direction']:10}"

            f"Close={obj['closeness']:.2f}  "

            f"Status={obj.get('status')}"

        )

    print("=" * 50)
    print("Suggested Path:", path)
    print("Speech:", speech)
    print("=" * 50)

    # ---------------------------------------
    # Return
    # ---------------------------------------

    return {

        "results": annotated_objects,

        "path": path,

        "speech": speech

    }