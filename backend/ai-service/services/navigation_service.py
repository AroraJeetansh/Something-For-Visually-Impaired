from transformers import pipeline
import numpy as np

# =====================================================
# LOAD DEPTH MODEL
# =====================================================

depth_estimator = pipeline(
    task="depth-estimation",
    model="depth-anything/Depth-Anything-V2-Small-hf",
    local_files_only=True
)

# =====================================================
# OBJECT PRIORITY
# Higher = More Important
# =====================================================

OBJECT_PRIORITY = {

    "person": 1.00,

    "stair": 0.95,

    "door": 0.80,

    "chair": 0.70,

    "table": 0.60

}


# =====================================================
# DIRECTION
# =====================================================

def get_direction(center_x, image_width):

    left = image_width / 3
    right = left * 2

    if center_x < left:
        return "left"

    elif center_x > right:
        return "right"

    return "center"


# =====================================================
# MAIN
# =====================================================

def analyze_navigation(image, detections):

    depth_result = depth_estimator(image)

    depth_map = np.array(
        depth_result["depth"]
    )

    depth_height, depth_width = depth_map.shape

    max_depth = float(
        np.max(depth_map)
    )

    navigation_results = []

    image_area = image.width * image.height

    for detection in detections:

        name = detection["name"]

        x1, y1, x2, y2 = detection["box"]

        # ---------------------------------------
        # Convert coordinates
        # ---------------------------------------

        x1_d = int(
            x1 * depth_width / image.width
        )

        x2_d = int(
            x2 * depth_width / image.width
        )

        y1_d = int(
            y1 * depth_height / image.height
        )

        y2_d = int(
            y2 * depth_height / image.height
        )

        region = depth_map[
            y1_d:y2_d,
            x1_d:x2_d
        ]

        if region.size == 0:
            continue

        # ---------------------------------------
        # DEPTH
        # ---------------------------------------

        median_depth = float(
            np.median(region)
        )

        closeness = 1 - (
            median_depth / max_depth
        )

        closeness = max(
            0,
            min(
                closeness,
                1
            )
        )

        # ---------------------------------------
        # BOX
        # ---------------------------------------

        box_width = x2 - x1

        box_height = y2 - y1

        box_area = box_width * box_height

        normalized_area = box_area / image_area

        # ---------------------------------------
        # DIRECTION
        # ---------------------------------------

        center_x = (x1 + x2) / 2

        direction = get_direction(
            center_x,
            image.width
        )

        # ---------------------------------------
        # OBJECT WEIGHT
        # ---------------------------------------

        object_weight = OBJECT_PRIORITY.get(
            name,
            0.50
        )

        # ---------------------------------------
        # FINAL PRIORITY
        # ---------------------------------------

        priority = (

            0.60 * closeness +

            0.30 * normalized_area +

            0.10 * object_weight

        )

        navigation_results.append({

            "object": name,

            "confidence": detection["confidence"],

            "direction": direction,

            "depth": round(
                median_depth,
                2
            ),

            "closeness": round(
                closeness,
                2
            ),

            "box_width": box_width,

            "box_height": box_height,

            "box_area": box_area,

            "priority": round(
                priority,
                3
            )

        })

    navigation_results.sort(

        key=lambda x: x["priority"],

        reverse=True

    )

    print("\nNavigation Ranking")

    print("=" * 50)

    for item in navigation_results:

        print(

            f"{item['object']:10}"

            f"Priority={item['priority']:.3f} "

            f"Depth={item['depth']:.1f} "

            f"{item['direction']}"

        )

    return navigation_results