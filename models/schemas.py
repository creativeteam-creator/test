from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Scene(BaseModel):
    scene_number: int
    text: str
    prompt: str
    characters: List[str] = Field(default_factory=list)


class ScriptParseRequest(BaseModel):
    script: str = Field(min_length=1)


class ScriptParseResponse(BaseModel):
    script_id: str
    characters: List[str]
    scenes: List[Scene]


class CharacterUploadResponse(BaseModel):
    character_id: str
    character_name: str
    image_url: str
    seed: int


class GenerateImagesRequest(BaseModel):
    script_id: str
    style_prompt: Optional[str] = "cinematic scene, ultra realistic"
    steps: int = 25
    cfg_scale: float = 7.0


class GeneratedSceneImage(BaseModel):
    scene_number: int
    image_path: str
    prompt: str


class GenerateImagesResponse(BaseModel):
    script_id: str
    images: List[GeneratedSceneImage]


class GenerateVideoRequest(BaseModel):
    script_id: str
    voice_name: Optional[str] = None


class GenerateVideoResponse(BaseModel):
    script_id: str
    audio_url: str
    video_url: str
    image_count: int


class CharacterRecord(BaseModel):
    character_id: str
    character_name: str
    image_path: str
    seed: int
    created_at: datetime


class ScriptRecord(BaseModel):
    script_id: str
    raw_script: str
    characters: List[str]
    scenes: List[Scene]
    created_at: datetime


class MediaRecord(BaseModel):
    script_id: str
    scene_images: List[str] = Field(default_factory=list)
    audio_path: Optional[str] = None
    video_path: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str


class CharacterSeedMap(BaseModel):
    seeds: Dict[str, int]
