const {
    analyzeImageWithGemini
} = require("../services/geminiService");

const analyzeImage = async (req, res) => {

    try {

        if (!req.file) {

            return res.status(400).json({
                success: false,
                error: "Image is required"
            });

        }

        const mode =
            req.body.mode || "scene";

        const language =
            req.body.language || "en";

        const result =
            await analyzeImageWithGemini(
                req.file,
                mode,
                language
            );

        return res.status(
            result.success ? 200 : 500
        ).json(result);

    } catch (error) {

        console.error(error);

        return res.status(500).json({
            success: false,
            error: "Internal Server Error"
        });

    }

};

module.exports = {
    analyzeImage
};