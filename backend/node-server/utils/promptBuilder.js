const getPrompt = (mode,language = "en") => {
    const languageInstruction =
    language === "hi"
    ?
    `
    Return all descriptions in Hindi.

    Examples:
    "आपके सामने एक कुर्सी है।"
    "कोई बाधा नहीं मिली।"
    `
    :
    `
    Return all descriptions in English.
    ` ;
    switch (mode) {

       case "ocr":
    return `
You are an OCR assistant.

Extract all visible text from the image.

Return ONLY valid JSON.

{
    "text_detected":""
}

Rules:
- Preserve paragraphs.
- Remove unnecessary line breaks caused by image formatting.
- Return clean readable text.
- If no text exists return exactly:
"No text detected"
`;


       case "obstacle":
    return `
You are assisting a visually impaired person.

Analyze the image for obstacles and navigation hazards.

Return ONLY valid JSON.

{
    "obstacle_warning":"",
    "safe_path":""
}

Rules:
- Be concise.
- Mention only important hazards.
- If none exist return:
"No obstacle detected"

${languageInstruction}

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
${languageInstruction}
`
;

    }
};

module.exports = getPrompt;