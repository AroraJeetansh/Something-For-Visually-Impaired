const {
    analyzeImageWithGemini
} = require(
    "../services/geminiService"
);

const analyzeImage = async (req, res) => {

    try {

        if (!req.file) {

            return res
                .status(400)
                .json({
                    error:
                        "Image is required"
                });
        }

        const mode =
            req.body.mode || "scene";
        const language = req.body.language || "en";
        const result =
            await analyzeImageWithGemini(
                req.file,
                mode,
                language
            );

        if (!result.success) {

            return res
                .status(500)
                .json({
                    error:
                        result.error
                });
        }
        res.json(result.data);

    } catch (error) {

        console.error(error);

        res.status(500).json({
            error:
                "Internal Server Error"
        });
    }
};

module.exports = {
    analyzeImage
};