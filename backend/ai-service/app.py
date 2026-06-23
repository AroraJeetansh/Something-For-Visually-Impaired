from fastapi import FastAPI

from routes.object_routes import router as object_router
from routes.navigation_routes import router as navigation_router
from routes.ocr_routes import router as ocr_router

app = FastAPI(
    title="ALIMCO AI Service"
)

app.include_router(object_router)
app.include_router(navigation_router)
app.include_router(ocr_router)