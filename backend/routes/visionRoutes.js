const express = require("express");
const router = express.Router();

const upload = require("../middleware/uploadMiddleware");
const {
  analyzeImage
} = require("../controllers/visionController");

router.post(
  "/analyze",
  upload.single("image"),
  analyzeImage
);

module.exports = router;