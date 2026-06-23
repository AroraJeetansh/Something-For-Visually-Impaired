const express = require("express");
const cors = require("cors");

require("dotenv").config();

const visionRoutes =
    require("./routes/visionRoutes");

const app = express();

app.use(cors());

app.use(express.json());

app.use(
    "/api/vision",
    visionRoutes
);

const PORT =
    process.env.PORT || 5000;

app.listen(PORT, () => {

    console.log(
        `Server running on port ${PORT}`
    );

});