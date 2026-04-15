from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from models.schemas import (
    GenerateImagesRequest,
    GenerateImagesResponse,
    GenerateVideoRequest,
    GenerateVideoResponse,
    MediaRecord,
)
from utils.config import settings
from utils.dependencies import image_generator_service, store, video_generator_service, voice_generator_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-images", response_model=GenerateImagesResponse)
async def generate_images(payload: GenerateImagesRequest) -> GenerateImagesResponse:
    script = store.get_script(payload.script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    missing = [name for name in script.characters if not store.get_character(name)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing character reference images: {', '.join(missing)}. Upload them with /characters/upload.",
        )

    records = [store.get_character(name) for name in script.characters]
    character_records = [r for r in records if r is not None]
    images = await image_generator_service.generate_scene_images(
        script_id=script.script_id,
        scenes=script.scenes,
        character_records=character_records,
        style_prompt=payload.style_prompt or "cinematic scene, ultra realistic",
        steps=payload.steps,
        cfg_scale=payload.cfg_scale,
    )

    media = store.get_media(script.script_id) or MediaRecord(script_id=script.script_id)
    media.scene_images = [img.image_path for img in images]
    store.save_media(media)

    return GenerateImagesResponse(script_id=script.script_id, images=images)


@router.post("/generate-video", response_model=GenerateVideoResponse)
async def generate_video(payload: GenerateVideoRequest) -> GenerateVideoResponse:
    script = store.get_script(payload.script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    media = store.get_media(payload.script_id)
    if not media or not media.scene_images:
        raise HTTPException(status_code=400, detail="No scene images found. Call /generate-images first")

    audio_path = await voice_generator_service.generate_voiceover(
        script_id=script.script_id,
        text=script.raw_script,
        voice_name=payload.voice_name,
    )
    video_path = await video_generator_service.create_video(
        script_id=script.script_id,
        image_paths=[Path(path) for path in media.scene_images],
        audio_path=audio_path,
    )

    media.audio_path = str(audio_path)
    media.video_path = str(video_path)
    store.save_media(media)

    return GenerateVideoResponse(
        script_id=script.script_id,
        audio_url=f"{settings.app_base_url}/storage/audio/{audio_path.name}",
        video_url=f"{settings.app_base_url}/storage/videos/{video_path.name}",
        image_count=len(media.scene_images),
    )
