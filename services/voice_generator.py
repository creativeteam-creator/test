from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

from google.cloud import texttospeech

from utils.config import settings

logger = logging.getLogger(__name__)


class VoiceGeneratorService:
    async def generate_voiceover(self, script_id: str, text: str, voice_name: str | None = None) -> Path:
        out_dir = settings.storage_dir / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{script_id}.mp3"

        await asyncio.to_thread(self._synthesize_to_path, text, output_path, voice_name)
        logger.info("Generated voiceover for script=%s at %s", script_id, output_path)
        return output_path

    def _synthesize_to_path(self, text: str, output_path: Path, voice_name: str | None) -> None:
        credentials = settings.google_tts_credentials_json.strip()
        if credentials:
            tmp_cred_path = output_path.with_suffix(".credentials.json")
            tmp_cred_path.write_text(credentials, encoding="utf-8")
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(tmp_cred_path)

        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=settings.default_voice_language_code,
            name=voice_name or settings.default_voice_name,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        output_path.write_bytes(response.audio_content)

        if credentials:
            cred_data = json.loads(settings.google_tts_credentials_json)
            if cred_data.get("type") == "service_account":
                try:
                    os.remove(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
                except OSError:
                    logger.warning("Could not remove temporary credential file", exc_info=True)
