from __future__ import annotations

import logging
import re
from typing import List

from models.schemas import Scene

logger = logging.getLogger(__name__)


class ScriptParserService:
    """Heuristic parser for MVP; replace with LLM/NLP parser in production."""

    CHARACTER_PATTERN = re.compile(r"\b([A-Z][A-Za-z]{2,})\b")

    async def parse_script(self, script: str) -> tuple[List[str], List[Scene]]:
        lines = [line.strip() for line in script.splitlines() if line.strip()]
        if not lines:
            return [], []

        scenes_text = self._split_into_scenes(lines)
        characters = self._extract_characters(script)

        scenes: List[Scene] = []
        for idx, scene_text in enumerate(scenes_text, start=1):
            scene_characters = [c for c in characters if re.search(rf"\b{re.escape(c)}\b", scene_text)]
            prompt = self._scene_to_prompt(scene_text, scene_characters)
            scenes.append(
                Scene(
                    scene_number=idx,
                    text=scene_text,
                    prompt=prompt,
                    characters=scene_characters,
                )
            )

        logger.info("Parsed script into %d scenes and %d characters", len(scenes), len(characters))
        return characters, scenes

    def _split_into_scenes(self, lines: List[str]) -> List[str]:
        scenes: List[List[str]] = [[]]
        for line in lines:
            if line.lower().startswith(("scene", "int.", "ext.")) and scenes[-1]:
                scenes.append([line])
            elif line == "---":
                if scenes[-1]:
                    scenes.append([])
            else:
                scenes[-1].append(line)

        return [" ".join(chunk).strip() for chunk in scenes if chunk]

    def _extract_characters(self, script: str) -> List[str]:
        candidates = self.CHARACTER_PATTERN.findall(script)
        blacklist = {
            "Scene",
            "INT",
            "EXT",
            "The",
            "And",
            "With",
            "From",
            "Then",
        }
        dedup = sorted({c for c in candidates if c not in blacklist})
        return dedup

    def _scene_to_prompt(self, scene_text: str, scene_characters: List[str]) -> str:
        character_text = ", ".join(scene_characters) if scene_characters else "no specific characters"
        return (
            f"cinematic scene, ultra realistic, {scene_text[:450]}, "
            f"featuring {character_text}, dramatic lighting, high detail"
        )
