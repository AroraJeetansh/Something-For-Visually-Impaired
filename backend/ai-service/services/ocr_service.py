from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="hi",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)


def extract_text(image_path):

    result = ocr.predict(
        image_path
    )

    texts = []

    for page in result:

        if "rec_texts" in page:

            texts.extend(
                page["rec_texts"]
            )

    return "\n".join(texts)