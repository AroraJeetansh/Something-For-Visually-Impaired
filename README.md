# AI-Powered Offline Smart Navigation Assistant Backend

An AI-powered backend developed for an Offline Smart Navigation Assistant designed to assist visually impaired users by analyzing their surroundings using Computer Vision and Artificial Intelligence.

The backend processes images captured by a client application and performs:

- Object Detection
- Monocular Depth Estimation
- Distance Classification
- Intelligent Path Planning
- Scene Memory
- Navigation Instruction Generation
- Optical Character Recognition (OCR)

The system has been designed with an offline-first architecture and serves as the core processing engine for future Android applications and wearable smart glasses.

---

# Features

## Object Detection

Detects common everyday objects along with navigation-specific obstacles using a customized YOLOv8 model.

Examples:

- Person
- Chair
- Bottle
- Door
- Staircase Up
- Staircase Down

---

## Depth Estimation

Generates a dense depth map from a single RGB image using **Depth Anything V2**, enabling relative distance estimation without requiring specialized hardware.

---

## Distance Estimation

Classifies detected objects into qualitative distance categories.

- Very Close
- Close
- Medium
- Far

---

## Intelligent Path Planning

Analyzes detected objects and recommends the safest navigation direction by evaluating:

- Object proximity
- Object size
- Navigation sector
- Risk score

---

## Scene Memory

Maintains contextual information across consecutive frames to reduce repetitive navigation instructions.

Object states include:

- New
- Still
- Approaching
- Moving Away

---

## Speech Generation

Produces concise navigation instructions such as:

> "Person ahead. Move slightly left."

> "Staircase on your right."

> "Continue straight."

---

## Optical Character Recognition (OCR)

Extracts printed text from images using PaddleOCR.

Example:

```json
{
  "text": "EXIT"
}
```

---

# Technology Stack

## Backend

- FastAPI
- Python

## Computer Vision

- Customized YOLOv8
- Depth Anything V2
- PaddleOCR
- Pillow (PIL)

## AI Libraries

- Ultralytics
- Hugging Face Transformers

## Development

- Swagger UI
- Git
- GitHub

---

# Backend Architecture

```text
Client Application
        │
        ▼
     FastAPI Backend
        │
        ▼
Object Detection (YOLOv8)
        │
        ▼
Depth Estimation
        │
        ▼
Distance Estimation
        │
        ▼
Path Planning
        │
        ▼
Scene Memory
        │
        ▼
Speech Generation
        │
        ▼
JSON Response
```

---

# Project Structure

```text
backend/
│
├── routes/
│   ├── navigation.py
│   ├── object_detection.py
│   └── ocr.py
│
├── services/
│   ├── object_detector.py
│   ├── depth_estimator.py
│   ├── distance_estimator.py
│   ├── path_planner.py
│   ├── scene_memory.py
│   ├── speech_service.py
│   ├── navigation_service.py
│   └── ocr_service.py
│
├── models/
│   └── combined.pt
│
├── main.py
│
└── requirements.txt
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/<username>/<repository>.git
cd backend
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Backend

```bash
uvicorn main:app --reload
```

The server will start at

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# Available APIs

## Navigation

```http
POST /navigation
```

Returns:

- Detected Objects
- Distance Labels
- Navigation Path
- Scene Memory Status
- Speech Instruction

---

## OCR

```http
POST /ocr
```

Returns extracted text from an uploaded image.

---

## Health Check

```http
GET /health
```

Returns the backend status.

---

# Sample Navigation Response

```json
{
  "results": [
    {
      "object": "person",
      "distance_label": "Close",
      "direction": "center",
      "status": "approaching"
    }
  ],
  "path": {
    "safe_direction": "left",
    "danger": true
  },
  "speech": "Person ahead. Move slightly left."
}
```

---

# Future Enhancements

- Android application integration
- Smart glasses integration
- Automatic session-based Scene Memory
- Real-time video navigation
- On-device model optimization
- Advanced navigation algorithms
- Handwritten OCR
- Voice interaction
- Visual Question Answering (VQA)

---

# Project Vision

The goal of this project is to build an intelligent, offline-first assistive navigation system capable of helping visually impaired users safely understand and navigate their surroundings using Artificial Intelligence and Computer Vision.

---

# Author

**Jeetansh Arora**

B.Tech Computer Science Engineering  
Jaypee University of Information Technology (JUIT)

---

⭐ If you found this project useful, consider starring the repository.
