from ultralytics import YOLO

model = YOLO("yolov8n.pt")

CONFIDENCE_THRESHOLD = 0.25


def detect_objects(image_path):

    results = model(image_path)

    detections = []

    for box in results[0].boxes:

        print(
        model.names[int(box.cls[0])],
        float(box.conf[0])
        )
    for box in results[0].boxes:

        confidence = float(
            box.conf[0]
        )

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        cls_id = int(
            box.cls[0]
        )

        detections.append({
            "name":
            model.names[cls_id],

            "confidence":
            round(confidence, 2),

            "box":
            list(
                map(
                    int,
                    box.xyxy[0]
                )
            )
        })

    return detections