const {
  analyzeImageWithGemini
} = require("../services/geminiService");

const analyzeImage = async (req, res) => {

  try {

      const mode = req.body.mode || "scene";

    const result =
      await analyzeImageWithGemini(req.file,
        mode
      );

    res.json(result);

  } catch (error) {

    res.status(500).json({
      error: error.message
    });

  }

};

module.exports = {
  analyzeImage
};