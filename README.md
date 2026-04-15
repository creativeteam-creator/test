# AI Video Generation SaaS Backend

FastAPI backend for script parsing, character image onboarding, Stable Diffusion image generation, Google TTS voiceover, and FFmpeg video assembly.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

## API Workflow

1. Parse script:

```bash
curl -X POST http://localhost:8000/scripts/parse \
  -H 'Content-Type: application/json' \
  -d '{"script":"Scene 1: Alice walks in the city at night. Bob meets Alice under neon lights. Scene 2: Bob and Alice run toward a rooftop helicopter."}'
```

2. Upload character reference images (one-time):

```bash
curl -X POST http://localhost:8000/characters/upload \
  -F 'character_name=Alice' \
  -F 'image=@./alice.png'

curl -X POST http://localhost:8000/characters/upload \
  -F 'character_name=Bob' \
  -F 'image=@./bob.png'
```

3. Generate scene images using Stable Diffusion + IP-Adapter/ControlNet:

```bash
curl -X POST http://localhost:8000/generate-images \
  -H 'Content-Type: application/json' \
  -d '{"script_id":"<SCRIPT_ID>","style_prompt":"cinematic scene, ultra realistic","steps":25,"cfg_scale":7}'
```

4. Generate final video (TTS + FFmpeg):

```bash
curl -X POST http://localhost:8000/generate-video \
  -H 'Content-Type: application/json' \
  -d '{"script_id":"<SCRIPT_ID>","voice_name":"en-US-Neural2-C"}'
```

Response includes downloadable URLs:

- `audio_url`: `/storage/audio/<script_id>.mp3`
- `video_url`: `/storage/videos/<script_id>.mp4`

## Notes

- Character consistency is handled by deterministic per-character seed and reference-image conditioning.
- Replace heuristic script parser with LLM parser for stronger production accuracy.
- Local JSON metadata store can be swapped with PostgreSQL/Redis without changing route contracts.
