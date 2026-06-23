from fastapi import APIRouter, UploadFile, File
from services.ocr_service import extract_text
from utils.image_utils import save_upload_file
from utils.response_utils import success_response
import os

router = APIRouter()


@router.post("/ocr")
async def ocr(
    image: UploadFile = File(...)
):

    filename = save_upload_file(image)

    try:

        text = extract_text(filename)

        if not text.strip():
            text = "No text detected"
        return success_response(
            "ocr",
            {
                "text": text,
                "speech": text
            }
        )

    finally:

        if os.path.exists(filename):
            os.remove(filename)