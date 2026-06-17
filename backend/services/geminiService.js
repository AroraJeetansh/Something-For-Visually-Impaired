const fs = require("fs");
const { GoogleGenAI } = require("@google/genai");
const getPrompt = require("../utils/promptBuilder");
require('dotenv').config()
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY
});

const analyzeImageWithGemini = async (file, mode = "scene") => {

    const imageBytes = fs.readFileSync(file.path);

    const base64Image = imageBytes.toString("base64");

    const prompt = getPrompt(mode);

    const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: [
            {
                inlineData: {
                    mimeType: file.mimetype,
                    data: base64Image
                }
            },
            {
                text: prompt
            }
        ]
    });

    const cleaned = response.text
        .replace(/```json/g, "")
        .replace(/```/g, "")
        .trim();

    return JSON.parse(cleaned);
};

module.exports = {
    analyzeImageWithGemini
};