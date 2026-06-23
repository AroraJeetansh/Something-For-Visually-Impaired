from transformers import pipeline
import numpy as np

depth_estimator = pipeline(
    task="depth-estimation",
    model="depth-anything/Depth-Anything-V2-Small-hf",
    local_files_only=True
)


def get_direction(box_center_x, image_width):

    if box_center_x < image_width * 0.33:
        return "left"

    elif box_center_x > image_width * 0.66:
        return "right"

    else:
        return "center"


def analyze_navigation(image, detections):

    result = depth_estimator(image)

    depth_map = np.array(result["depth"])

    depth_h, depth_w = depth_map.shape

    navigation_results = []

    for detection in detections:

        name = detection["name"]

        x1, y1, x2, y2 = detection["box"]

        # Convert YOLO coordinates
        x1_d = int(x1 * depth_w / image.width)
        x2_d = int(x2 * depth_w / image.width)

        y1_d = int(y1 * depth_h / image.height)
        y2_d = int(y2 * depth_h / image.height)

        region = depth_map[y1_d:y2_d, x1_d:x2_d]

        if region.size == 0:
            continue

        avg_depth = np.median(region)
        # Bounding box metrics
        box_width = x2 - x1
        box_height = y2 - y1
        box_area = box_width * box_height

        # Direction
        box_center_x = (x1 + x2) / 2

        direction = get_direction(
            box_center_x,
            image.width
        )

        # Combined score
        image_area = image.width * image.height

        normalized_area = box_area / image_area

        score = (
        avg_depth * 0.5
            +
        normalized_area * 255 * 0.5
                                    )

        print("\n========================")
        print("Object:", name)
        print("Depth:", round(avg_depth, 2))
        print("Width:", box_width)
        print("Height:", box_height)
        print("Area:", box_area)
        print("Direction:", direction)
        print("Score:", round(score, 2))

        navigation_results.append({
            "object": name,
            "depth": round(avg_depth, 2),
            "box_width": box_width,
            "box_height": box_height,
            "box_area": box_area,
            "score": round(score, 2),
            "direction": direction
        })

    # Highest score first
    navigation_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return navigation_results