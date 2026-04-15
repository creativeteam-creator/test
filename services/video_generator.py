from __future__ import annotations

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import List

from utils.config import settings

logger = logging.getLogger(__name__)


class VideoGeneratorService:
    async def create_video(self, script_id: str, image_paths: List[Path], audio_path: Path) -> Path:
        output_dir = settings.storage_dir / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{script_id}.mp4"

        await asyncio.to_thread(self._run_ffmpeg, output_path, image_paths, audio_path)
        logger.info("Created final video at %s", output_path)
        return output_path

    def _run_ffmpeg(self, output_path: Path, image_paths: List[Path], audio_path: Path) -> None:
        if not image_paths:
            raise ValueError("No images provided for video generation")

        total_audio_duration = self._audio_duration(audio_path)
        per_image_duration = max(total_audio_duration / len(image_paths), 0.5)

        concat_file = output_path.with_suffix(".txt")
        lines = []
        for path in image_paths:
            lines.append(f"file '{path.resolve()}'")
            lines.append(f"duration {per_image_duration}")
        lines.append(f"file '{image_paths[-1].resolve()}'")
        concat_file.write_text("\n".join(lines), encoding="utf-8")

        cmd = [
            settings.ffmpeg_path,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-i",
            str(audio_path),
            "-vf",
            "fps=24,format=yuv420p",
            "-shortest",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output_path),
        ]

        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            logger.error("FFmpeg failed: %s", completed.stderr)
            raise RuntimeError(f"FFmpeg failed: {completed.stderr}")

    def _audio_duration(self, audio_path: Path) -> float:
        cmd = [
            settings.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {completed.stderr}")
        return float(completed.stdout.strip())
