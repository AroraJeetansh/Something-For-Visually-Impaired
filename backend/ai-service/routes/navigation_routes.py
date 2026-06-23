from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from PIL import Image

from services.object_detector import (
    detect_objects
)

from services.navigation_service import (
    analyze_navigation
)

from utils.image_utils import (
    save_upload_file
)
from utils.response_utils import (
    success_response
)

from utils.speech_utils import (
    build_navigation_speech
)

import os

router = APIRouter()


@router.post("/navigation")
async def navigation(
    image: UploadFile = File(...)
):

    filename = save_upload_file(image)

    try:

        detections = detect_objects(
            filename
        )

        image_pil = Image.open(
            filename
        )

        results = analyze_navigation(
            image_pil,
            detections
        )
        speech = build_navigation_speech(
            results
        )

        return success_response(
        "navigation",
            {
            "results": results,
            "speech": speech
             })

    finally:

        if os.path.exists(filename):
            os.remove(filename)


        