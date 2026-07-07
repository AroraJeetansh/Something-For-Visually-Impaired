from ultralytics import YOLO
import time

# =====================================================
# LOAD MODEL
# =====================================================

model = YOLO("models/combined.pt")   # Change filename if needed

CONFIDENCE_THRESHOLD = 0.25

# =====================================================
# PARSE YOLO RESULTS
# =====================================================

def parse_results(results):

    detections = []

    for box in results[0].boxes:

        confidence = float(box.conf[0])

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        cls_id = int(box.cls[0])

        detections.append({

            "name": model.names[cls_id],

            "confidence": round(confidence, 2),

            "box": list(
                map(
                    int,
                    box.xyxy[0]
                )
            )

        })

    return detections


# =====================================================
# MAIN FUNCTION
# =====================================================

def detect_objects(image_path):

    print("\nStarting Object Detection...")

    start = time.time()

    results = model(
        image_path,
        verbose=False
    )

    inference_time = time.time() - start

    print(
        f"YOLO Inference    : {inference_time:.2f}s"
    )

    detections = parse_results(results)

    print(
        f"Objects Detected  : {len(detections)}"
    )

    print("\nDetected Objects")
    print("=" * 40)

    for detection in detections:

        print(
            f"{detection['name']:20}"
            f"{detection['confidence']}"
        )

    return detections