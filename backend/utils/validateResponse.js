const validateResponse = (data, mode) => {

    if (mode === "ocr") {

        return {
            text_detected:
                data.text_detected ||
                "No text detected"
        };
    }

    if (mode === "obstacle") {

        return {
            obstacle_warning:
                data.obstacle_warning ||
                "No obstacle detected",

            safe_path:
                data.safe_path ||
                "No guidance available"
        };
    }

    return {
        scene_description:
            data.scene_description ||
            "Scene description unavailable",

        text_detected:
            data.text_detected ||
            "No text detected",

        objects:
            data.objects || [],

        obstacle_warning:
            data.obstacle_warning ||
            "No obstacle detected"
    };
};

module.exports = validateResponse;