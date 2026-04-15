from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.script import router as script_router
from routes.character import router as character_router
from routes.video import router as video_router
from utils.config import settings
from utils.logger import configure_logging

configure_logging()

app = FastAPI(
    title="AI Video Generation SaaS Backend",
    version="1.0.0",
    description="Production-ready backend for script parsing, character management, image generation, voiceover, and final video assembly.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(script_router, prefix="/scripts", tags=["scripts"])
app.include_router(character_router, prefix="/characters", tags=["characters"])
app.include_router(video_router, tags=["video-generation"])

app.mount("/storage", StaticFiles(directory="storage"), name="storage")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
