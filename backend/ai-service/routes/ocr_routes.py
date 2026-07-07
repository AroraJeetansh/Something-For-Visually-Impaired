import os
import time

from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from services.ocr_service import (
    extract_text
)

from utils.image_utils import (
    save_upload_file
)

from utils.response_utils import (
    success_response
)

router = APIRouter()


@router.post("/ocr")
async def ocr(
    image: UploadFile = File(...)
):

    filename = save_upload_file(image)

    start = time.time()

    try:

        texts = extract_text(
            filename
        )

        print(
            f"OCR Time: {time.time()-start:.2f}s"
        )

        if len(texts) == 0:

            speech = "No text detected."

        else:

            speech = " ".join(texts)

        return success_response(

            "ocr",

            {

                "texts": texts,

                "speech": speech

            }

        )

    finally:

        if os.path.exists(filename):

            os.remove(filename)