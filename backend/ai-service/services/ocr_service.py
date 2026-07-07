import os
import tempfile

from PIL import Image
from paddleocr import PaddleOCR

# =====================================================
# LOAD OCR
# =====================================================
#
# Speed tuning notes (why these params changed):
#
# 1. enable_mkldnn=True, cpu_threads=4
#    Explicitly turns on Intel's oneDNN CPU acceleration and lets
#    PaddleOCR use multiple threads. The "ReduceMeanCheckIfOneDNNSupport"
#    spam in your logs is PaddleOCR checking oneDNN support per-op --
#    explicitly enabling it (rather than relying on default detection)
#    avoids redundant checks and lets it actually use the fast path.
#
# 2. text_det_limit_side_len=480
#    Caps the detection model's internal resize. PaddleOCR's text
#    detector resizes internally regardless of your input size, and by
#    default uses a large side length tuned for accuracy over speed.
#    On an i3 CPU this is usually the single biggest cost. Lowering
#    this trades a little accuracy on very small/dense text for a
#    large speed gain -- reasonable for a navigation-priority app
#    where OCR is "good enough" not "perfect."
#
# 3. MAX_SIZE lowered 960 -> 640
#    Matches the smaller detection side length; resizing to 960 first
#    just to have the detector immediately downscale further internally
#    wastes time on the resize itself.
#
# 4. text_detection_model_name / text_recognition_model_name pinned to
#    "_mobile_" variants.
#    Recent PaddleOCR versions changed the DEFAULT models for detection
#    and recognition from mobile to server variants -- server models
#    are significantly larger/slower and meant for GPU or beefy CPU
#    deployments. On an i3, this is likely the single biggest reason
#    OCR is taking 18s. Pinning explicitly to mobile models avoids
#    silently inheriting that heavier default in future upgrades too.
#
# Everything else (use_doc_orientation_classify=False, etc.) is kept
# as-is since you already had those disabled correctly.

ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    text_det_limit_side_len=480,
    enable_mkldnn=True,
    cpu_threads=4
)

MAX_SIZE = 640


# =====================================================
# RESIZE IMAGE
# =====================================================

def prepare_image(image_path):

    image = Image.open(image_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.thumbnail(
        (MAX_SIZE, MAX_SIZE),
        Image.Resampling.LANCZOS
    )

    temp = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    temp_path = temp.name

    temp.close()

    image.save(
        temp_path,
        "JPEG",
        quality=85
    )

    return temp_path


# =====================================================
# OCR
# =====================================================

def extract_text(image_path):

    temp_path = prepare_image(image_path)

    try:

        result = ocr.predict(temp_path)

        texts = []

        for page in result:

            rec_texts = page.get(
                "rec_texts",
                []
            )

            rec_scores = page.get(
                "rec_scores",
                []
            )

            for text, score in zip(
                rec_texts,
                rec_scores
            ):

                if score < 0.50:
                    continue

                text = " ".join(
                    text.split()
                )

                if len(text) > 1:

                    texts.append(text)

        return texts

    finally:

        if os.path.exists(temp_path):

            os.remove(temp_path)