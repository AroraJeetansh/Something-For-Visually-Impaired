const express = require("express");
const cors = require("cors");
const visionRoutes = require("./routes/visionRoutes");
require("dotenv").config();
const app = express();
app.use(cors());
app.use(express.json());

app.use("/api/vision", visionRoutes);

app.listen(5000, () => {
  console.log("Server running");
});