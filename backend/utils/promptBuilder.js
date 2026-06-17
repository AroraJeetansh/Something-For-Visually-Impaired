const getPrompt = (mode = "scene") => {

    switch (mode) {

        case "ocr":
            return `
Extract all visible text from the image.

Return ONLY JSON:

{
    "text_detected": ""
}
`;

        case "obstacle":
            return `
You are assisting a visually impaired user.

Identify obstacles and safety hazards.

Return ONLY JSON:

{
    "obstacle_warning": "",
    "objects": []
}
`;

        case "scene":
        default:
            return `
You are an AI assistant for visually impaired users.

Analyze the image and return ONLY valid JSON.

{
    "scene_description": "",
    "text_detected": "",
    "objects": [],
    "obstacle_warning": ""
}

Rules:
- scene_description under 20 words
- objects should be simple names
- obstacle_warning should be short
- no markdown
- no explanations
`;
    }
};

module.exports = getPrompt;