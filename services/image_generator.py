from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import List

import httpx

from models.schemas import CharacterRecord, GeneratedSceneImage, Scene
from utils.config import settings

logger = logging.getLogger(__name__)


class ImageGeneratorService:
    def __init__(self) -> None:
        self.base_url = settings.sd_base_url.rstrip("/")
        self.timeout = settings.sd_timeout_seconds

    async def generate_scene_images(
        self,
        script_id: str,
        scenes: List[Scene],
        character_records: List[CharacterRecord],
        style_prompt: str,
        steps: int,
        cfg_scale: float,
    ) -> List[GeneratedSceneImage]:
        out_dir = settings.storage_dir / "images" / script_id
        out_dir.mkdir(parents=True, exist_ok=True)

        character_map = {c.character_name.lower(): c for c in character_records}
        generated: List[GeneratedSceneImage] = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for scene in scenes:
                seed = self._seed_for_scene(scene, character_map)
                init_refs = [character_map[c.lower()] for c in scene.characters if c.lower() in character_map]
                payload = self._build_payload(scene.prompt, style_prompt, seed, steps, cfg_scale, init_refs)

                logger.info("Generating image for script=%s scene=%s", script_id, scene.scene_number)
                response = await client.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload)
                response.raise_for_status()
                data = response.json()
                images = data.get("images", [])
                if not images:
                    raise RuntimeError(f"No images returned from Stable Diffusion for scene {scene.scene_number}")

                image_bytes = base64.b64decode(images[0])
                image_path = out_dir / f"scene_{scene.scene_number:03d}.png"
                image_path.write_bytes(image_bytes)

                generated.append(
                    GeneratedSceneImage(
                        scene_number=scene.scene_number,
                        image_path=str(image_path),
                        prompt=payload["prompt"],
                    )
                )

        return generated

    def _seed_for_scene(self, scene: Scene, character_map: dict[str, CharacterRecord]) -> int:
        for name in scene.characters:
            if name.lower() in character_map:
                return character_map[name.lower()].seed
        return 123456

    def _build_payload(
        self,
        scene_prompt: str,
        style_prompt: str,
        seed: int,
        steps: int,
        cfg_scale: float,
        references: List[CharacterRecord],
    ) -> dict:
        ip_adapter_args = []
        for ref in references:
            image_b64 = base64.b64encode(Path(ref.image_path).read_bytes()).decode("utf-8")
            ip_adapter_args.append(
                {
                    "image": image_b64,
                    "weight": 0.8,
                    "model": "ip-adapter-plus-face_sd15",
                }
            )

        prompt = f"{style_prompt}, {scene_prompt}"

        payload = {
            "prompt": prompt,
            "negative_prompt": "blurry, deformed, lowres, bad anatomy",
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "width": 768,
            "height": 432,
            "sampler_name": "DPM++ 2M Karras",
        }

        if ip_adapter_args:
            payload["alwayson_scripts"] = {
                "controlnet": {
                    "args": [
                        {
                            "input_image": entry["image"],
                            "module": "ip-adapter-auto",
                            "model": entry["model"],
                            "weight": entry["weight"],
                            "resize_mode": "Crop and Resize",
                            "processor_res": 512,
                            "enabled": True,
                        }
                        for entry in ip_adapter_args
                    ]
                }
            }

        return payload
