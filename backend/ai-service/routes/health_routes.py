from fastapi import APIRouter

router = APIRouter()

@router.get("/health")

async def health():

    return {
        "status": "ok",
        "services": {
            "ocr": True,
            "object_detection": True,
            "navigation": True
        }
    }