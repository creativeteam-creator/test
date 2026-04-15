from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from models.schemas import CharacterRecord, CharacterUploadResponse
from utils.config import settings
from utils.dependencies import store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=CharacterUploadResponse)
async def upload_character_image(
    character_name: str = Form(...),
    image: UploadFile = File(...),
) -> CharacterUploadResponse:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    char_id = str(uuid4())
    suffix = Path(image.filename or "character.png").suffix or ".png"
    out_dir = settings.storage_dir / "characters"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{char_id}{suffix}"

    content = await image.read()
    out_path.write_bytes(content)

    seed = _seed_from_name(character_name)
    record = CharacterRecord(
        character_id=char_id,
        character_name=character_name.strip(),
        image_path=str(out_path),
        seed=seed,
        created_at=datetime.now(tz=timezone.utc),
    )
    store.save_character(record)

    logger.info("Character image uploaded for %s", character_name)
    return CharacterUploadResponse(
        character_id=char_id,
        character_name=record.character_name,
        image_url=f"{settings.app_base_url}/storage/characters/{out_path.name}",
        seed=seed,
    )


@router.get("/")
async def list_characters() -> list[CharacterUploadResponse]:
    records = store.list_characters()
    result = []
    for record in records.values():
        image_name = Path(record.image_path).name
        result.append(
            CharacterUploadResponse(
                character_id=record.character_id,
                character_name=record.character_name,
                image_url=f"{settings.app_base_url}/storage/characters/{image_name}",
                seed=record.seed,
            )
        )
    return result


def _seed_from_name(name: str) -> int:
    digest = hashlib.sha256(name.lower().strip().encode("utf-8")).hexdigest()[:8]
    return int(digest, 16)
