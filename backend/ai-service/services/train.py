from ultralytics import YOLO

# Load pretrained model
model = YOLO("yolov8n.pt")

# Train
model.train(
    data="D:/ALIMCO_Visual_Glasses/backend/ai-service/services/Navigation_Assist.v2i.yolov8/data.yaml",

    epochs=50,

    imgsz=640,

    batch=16,

    workers=4,

    project="runs",

    name="navigation",

    exist_ok=True,

    patience=15,
    pretrained=True,

    optimizer="auto",

    device="cpu"
)