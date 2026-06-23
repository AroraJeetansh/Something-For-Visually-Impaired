const { GoogleGenAI } = require("@google/genai");

const getPrompt = require("../utils/promptBuilder");
const cleanGeminiResponse = require("../utils/responseCleaner");
const validateResponse = require("../utils/validateResponse");

require('dotenv').config()
const ai = new GoogleGenAI({
    apiKey: process.env.GEMINI_API_KEY
});

const analyzeImageWithGemini =
async (
    file,
    mode = "scene",
    language = "en"
) => {

    try {

        const base64Image =
            file.buffer.toString("base64");


        const prompt = getPrompt(mode, language)

        const response =
            await ai.models.generateContent({

                model: "gemini-2.5-flash",

                contents: [
                    {
                        inlineData: {
                            mimeType:
                                file.mimetype,

                            data:
                                base64Image
                        }
                    },
                    {
                        text: prompt
                    }
                ]
            });

        const cleaned =
            cleanGeminiResponse(
                response.text
            );

        let parsed;

        try {

            parsed =
                JSON.parse(cleaned);
               if (parsed.text_detected) {

            parsed.text_detected = parsed.text_detected
            .replace(/(?<!\n)\n(?!\n)/g, " ")
            .trim();
}

        } catch {

            throw new Error(
                "Gemini returned invalid JSON"
            );
        }

        return {
            success: true,
            data:
                validateResponse(
                    parsed,
                    mode
                )
        };

    } catch (error) {

        console.error(
            "Gemini Service Error:",
            error
        );

        return {
            success: false,
            error:
                error.message ||
                "Failed to analyze image"
        };
    }
};

module.exports = {
    analyzeImageWithGemini
};