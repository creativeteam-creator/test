from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from models.schemas import CharacterRecord, MediaRecord, ScriptRecord


class JsonStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"characters": {}, "scripts": {}, "media": {}}, indent=2), encoding="utf-8")

    def _read(self) -> Dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, payload: Dict) -> None:
        self.path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def save_character(self, record: CharacterRecord) -> None:
        with self._lock:
            payload = self._read()
            payload["characters"][record.character_name.lower()] = record.model_dump(mode="json")
            self._write(payload)

    def get_character(self, name: str) -> Optional[CharacterRecord]:
        payload = self._read()
        raw = payload["characters"].get(name.lower())
        if not raw:
            return None
        return CharacterRecord.model_validate(raw)

    def list_characters(self) -> Dict[str, CharacterRecord]:
        payload = self._read()
        return {k: CharacterRecord.model_validate(v) for k, v in payload["characters"].items()}

    def save_script(self, record: ScriptRecord) -> None:
        with self._lock:
            payload = self._read()
            payload["scripts"][record.script_id] = record.model_dump(mode="json")
            self._write(payload)

    def get_script(self, script_id: str) -> Optional[ScriptRecord]:
        payload = self._read()
        raw = payload["scripts"].get(script_id)
        if not raw:
            return None
        return ScriptRecord.model_validate(raw)

    def save_media(self, record: MediaRecord) -> None:
        with self._lock:
            payload = self._read()
            payload["media"][record.script_id] = record.model_dump(mode="json")
            self._write(payload)

    def get_media(self, script_id: str) -> Optional[MediaRecord]:
        payload = self._read()
        raw = payload["media"].get(script_id)
        if not raw:
            return None
        return MediaRecord.model_validate(raw)
