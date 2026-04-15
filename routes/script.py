from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from models.schemas import ScriptParseRequest, ScriptParseResponse, ScriptRecord
from utils.dependencies import script_parser_service, store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/parse", response_model=ScriptParseResponse)
async def parse_script(payload: ScriptParseRequest) -> ScriptParseResponse:
    characters, scenes = await script_parser_service.parse_script(payload.script)
    if not scenes:
        raise HTTPException(status_code=400, detail="Unable to parse script into scenes")

    script_id = str(uuid4())
    record = ScriptRecord(
        script_id=script_id,
        raw_script=payload.script,
        characters=characters,
        scenes=scenes,
        created_at=datetime.now(tz=timezone.utc),
    )
    store.save_script(record)

    logger.info("Script parsed and stored: %s", script_id)
    return ScriptParseResponse(script_id=script_id, characters=characters, scenes=scenes)


@router.get("/{script_id}", response_model=ScriptParseResponse)
async def get_script(script_id: str) -> ScriptParseResponse:
    record = store.get_script(script_id)
    if not record:
        raise HTTPException(status_code=404, detail="Script not found")
    return ScriptParseResponse(script_id=record.script_id, characters=record.characters, scenes=record.scenes)
