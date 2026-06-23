from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from services.object_detector import (
    detect_objects
)

from utils.image_utils import (
    save_upload_file
)

from utils.response_utils import (
    success_response,
    error_response
)

import os

router = APIRouter()


@router.post("/objects")
async def objects(
    image: UploadFile = File(...)
):

    filename = save_upload_file(image)

    try:

        detections = detect_objects(
            filename
        )

        return success_response(
            "objects",
            {
                "objects": detections
            }
        )

    finally:

        if os.path.exists(filename):
            os.remove(filename)