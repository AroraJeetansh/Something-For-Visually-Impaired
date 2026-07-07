import os
import time

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

from services.scene_memory import SceneMemory

from utils.image_utils import (
    save_upload_file
)

from utils.response_utils import (
    success_response
)

router = APIRouter()

# Single shared memory instance for the MVP (one user/device at a
# time). If this ever needs to support multiple simultaneous users,
# this becomes a dict keyed by some client identifier instead.
scene_memory = SceneMemory()


@router.post("/navigation")
async def navigation(
    image: UploadFile = File(...)
):

    filename = save_upload_file(image)

    total_start = time.time()

    try:

        image_pil = Image.open(filename)

        print("\n" + "=" * 60)
        print("NEW NAVIGATION REQUEST")
        print("=" * 60)
        print("Image Size:", image_pil.size)

        # ---------------------------------------
        # Object Detection
        # ---------------------------------------

        start = time.time()

        detections = detect_objects(
            filename
        )

        print(
            f"\nObject Detection : "
            f"{time.time()-start:.2f}s"
        )

        # ---------------------------------------
        # Navigation
        # ---------------------------------------

        start = time.time()

        navigation_result = analyze_navigation(
            image_pil,
            detections,
            scene_memory
        )

        print(
            f"Navigation Logic : "
            f"{time.time()-start:.2f}s"
        )

        print(
            f"TOTAL REQUEST : "
            f"{time.time()-total_start:.2f}s"
        )

        print("=" * 60)

        return success_response(

            "navigation",

            navigation_result

        )

    finally:

        if os.path.exists(filename):

            os.remove(filename)


@router.post("/navigation/reset")
async def navigation_reset():
    """
    Clears scene memory. Call this when starting a fresh walk so
    stale object tracking from a previous session doesn't bleed in.
    """

    scene_memory.reset()

    return success_response(
        "navigation_reset",
        {}
    )