from pathlib import Path

from models.store import JsonStore
from services.ai_parser import ScriptParserService
from services.image_generator import ImageGeneratorService
from services.video_generator import VideoGeneratorService
from services.voice_generator import VoiceGeneratorService
from utils.config import settings

store = JsonStore(Path(settings.storage_dir) / "metadata.json")
script_parser_service = ScriptParserService()
image_generator_service = ImageGeneratorService()
voice_generator_service = VoiceGeneratorService()
video_generator_service = VideoGeneratorService()
