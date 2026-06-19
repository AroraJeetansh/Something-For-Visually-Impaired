# Smart Vision Assistant Backend

An AI-powered backend for a Smart Vision Assistant designed to help visually impaired users understand and navigate their surroundings through image analysis.

The system leverages **Google Gemini Vision** to provide:

- OCR (Text Reading)
- Scene Understanding
- Obstacle Awareness
- Object Identification

This backend is designed to be integrated with future platforms such as:

- Smart Glasses
- Mobile Applications
- Wearable Devices
- Accessibility Assistants

---

## Features

### Scene Analysis

Provides a concise description of the environment.

**Example Response**

```json
{
  "scene_description": "Blue bird perched on a flowering branch.",
  "text_detected": "No text detected",
  "objects": [
    "bird",
    "flowers",
    "branch"
  ],
  "obstacle_warning": "No obstacle detected"
}
```

---

### OCR Mode

Extracts all visible text from an image.

**Example Response**

```json
{
  "text_detected": "Welcome to JUIT"
}
```

---

### Obstacle Detection Mode

Identifies potential navigation hazards.

**Example Response**

```json
{
  "obstacle_warning": "Chair ahead",
  "safe_path": "Move slightly right"
}
```

---

## Tech Stack

### Backend

- Node.js
- Express.js

### AI

- Google Gemini 2.5 Flash Vision

### File Handling

- Multer

### Environment Management

- dotenv

---

## Project Structure

```text
backend/
│
├── server.js
│
├── routes/
│   └── visionRoutes.js
│
├── controllers/
│   └── visionController.js
│
├── services/
│   └── geminiService.js
│
├── middleware/
│   └── uploadMiddleware.js
│
├── utils/
│   └── promptBuilder.js
│
├── uploads/
│
├── .env
│
└── package.json
```

---

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd backend
```

### Install Dependencies

```bash
npm install
```

---

## Environment Variables

Create a `.env` file in the root directory.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Get your API key from:

https://aistudio.google.com/

---

## Running the Server

Start the application:

```bash
node server.js
```

Server will run on:

```text
http://localhost:5000
```

---

## API Endpoint

### Analyze Image

```http
POST /api/vision/analyze
```

### Content Type

```text
multipart/form-data
```

### Parameters

| Parameter | Type | Description |
|------------|------|-------------|
| image | File | Image to analyze |
| mode | String | scene, ocr, obstacle |

---

## Scene Mode

### Request

```text
mode=scene
```

### Response

```json
{
  "scene_description": "Person sitting at a desk.",
  "text_detected": "No text detected",
  "objects": [
    "person",
    "laptop",
    "chair"
  ],
  "obstacle_warning": "No obstacle detected"
}
```

---

## OCR Mode

### Request

```text
mode=ocr
```

### Response

```json
{
  "text_detected": "Department of Computer Science"
}
```

---

## Obstacle Mode

### Request

```text
mode=obstacle
```

### Response

```json
{
  "obstacle_warning": "Table ahead",
  "safe_path": "Move slightly left"
}
```

---

## Testing with Postman

1. Create a **POST** request
2. URL:

```text
http://localhost:5000/api/vision/analyze
```

3. Select **Body → form-data**
4. Add:

| Key | Type | Value |
|------|------|------|
| image | File | Upload image |
| mode | Text | scene / ocr / obstacle |

5. Click **Send**

---

## Future Enhancements

- Real-time video analysis
- Voice commands
- Text-to-Speech feedback
- Mobile application integration
- Smart glasses integration
- Face recognition
- Currency recognition
- Indoor navigation assistance
- Offline AI inference

---

## Project Vision

The long-term vision of this project is to develop an intelligent wearable assistant capable of helping visually impaired individuals understand, interpret, and navigate the world around them using AI-powered computer vision and natural language technologies.

---

## Author

**Jeetansh Arora**

B.Tech Computer Science Engineering  
Jaypee University of Information Technology (JUIT)

---

### If you find this project useful, consider starring the repository.
