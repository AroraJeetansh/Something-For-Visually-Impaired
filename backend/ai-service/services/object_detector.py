from ultralytics import YOLO

# =====================================================
# LOAD MODELS
# =====================================================

general_model = YOLO("models/yolov8n.pt")

navigation_model = YOLO(
    "models/navigation.pt"
)

CONFIDENCE_THRESHOLD = 0.25


IOU_THRESHOLD = 0.60


# =====================================================
# IOU
# =====================================================

def calculate_iou(box1, box2):

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    if x2 <= x1 or y2 <= y1:
        return 0.0

    intersection = (x2 - x1) * (y2 - y1)

    area1 = (
        (box1[2] - box1[0]) *
        (box1[3] - box1[1])
    )

    area2 = (
        (box2[2] - box2[0]) *
        (box2[3] - box2[1])
    )

    union = area1 + area2 - intersection

    return intersection / union


# =====================================================
# PARSE YOLO RESULTS
# =====================================================

def parse_results(results, names):

    detections = []

    for box in results[0].boxes:

        confidence = float(box.conf[0])

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        cls_id = int(box.cls[0])

        detections.append({

            "name": names[cls_id],

            "confidence": round(
                confidence,
                2
            ),

            "box": list(
                map(
                    int,
                    box.xyxy[0]
                )
            )

        })

    return detections


# =====================================================
# REMOVE DUPLICATES
# =====================================================

def remove_duplicates(detections):

    filtered = []

    detections = sorted(
        detections,
        key=lambda x: x["confidence"],
        reverse=True
    )

    for detection in detections:

        duplicate = False

        for kept in filtered:

            if detection["name"] != kept["name"]:
                continue

            iou = calculate_iou(
                detection["box"],
                kept["box"]
            )

            if iou > IOU_THRESHOLD:

                duplicate = True
                break

        if not duplicate:
            filtered.append(detection)

    return filtered


# =====================================================
# MAIN FUNCTION
# =====================================================

def detect_objects(image_path):

    general_results = general_model(
        image_path,
        verbose=False
    )

    navigation_results = navigation_model(
        image_path,
        verbose=False
    )

    detections = []

    detections.extend(
        parse_results(
            general_results,
            general_model.names
        )
    )

    detections.extend(
        parse_results(
            navigation_results,
            navigation_model.names
        )
    )

    detections = remove_duplicates(
        detections
    )

    print("\nDetected Objects")

    print("=" * 40)

    for detection in detections:

        print(

            f"{detection['name']:12}"

            f"{detection['confidence']}"

        )

    return detections