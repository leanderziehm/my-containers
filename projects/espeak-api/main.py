
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Query

app = FastAPI(title="eSpeak TTS API")

# Open CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str = "en-us"
    speed: int = Field(default=150, ge=80, le=450)
    pitch: int = Field(default=50, ge=0, le=99)


# Serve index.html and other static assets
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post("/tts")
def generate_speech(request: TTSRequest):
    try:
        result = subprocess.run(
            [
                "espeak-ng",
                "--stdout",
                "-v", request.voice,
                "-s", str(request.speed),
                "-p", str(request.pitch),
                request.text,
            ],
            capture_output=True,
            timeout=30,
            check=True,
        )

        return Response(
            content=result.stdout,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="speech.wav"'
            },
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Speech generation timed out")

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Speech generation failed")






# --------------------------------------------------
# GET ALL ESPEAK VOICES
# --------------------------------------------------

@app.get("/voices")
def get_voices(
    variant: str | None = Query(
        default=None,
        description="Optional language filter, e.g. en, en-us, de, fr, mb"
    )
):
    try:
        result = subprocess.run(
            ["espeak-ng", "--voices=all"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )

        voices = []

        for line in result.stdout.splitlines():

            parts = line.split(maxsplit=5)

            # Skip headers and invalid lines
            if len(parts) < 5:
                continue

            priority, language, gender, name, filename = parts[:5]

            other_languages = parts[5] if len(parts) > 5 else ""

            voices.append({
                "priority": priority,
                "language": language,
                "gender": gender,
                "name": name,
                "file": filename,
                "other_languages": other_languages,
            })

        # Optional language/variant filtering
        if variant:
            variant = variant.strip().lower()

            voices = [
                voice for voice in voices
                if (
                    voice["language"].lower() == variant
                    or voice["language"].lower().startswith(variant + "-")
                    or voice["language"].lower().startswith(variant + "_")
                )
            ]

        return {
            "count": len(voices),
            "variant": variant,
            "voices": voices,
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="espeak-ng executable not found"
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Voice listing timed out"
        )

    except subprocess.CalledProcessError:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve eSpeak voices"
        )



@app.get("/voices/languages")
def get_languages():
    try:
        result = subprocess.run(
            ["espeak-ng", "--voices=all"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )

        languages = {}

        for line in result.stdout.splitlines():
            parts = line.split(maxsplit=5)

            if len(parts) < 5:
                continue

            language = parts[1].lower()

            # Group regional variants under their main language
            code = language.split("-")[0]

            if code not in languages:
                languages[code] = {
                    "code": code,
                    "name": {
                        "en": "English",
                        "de": "German",
                        "fr": "French",
                        "es": "Spanish",
                        "it": "Italian",
                        "pt": "Portuguese",
                        "ru": "Russian",
                        "ja": "Japanese",
                        "zh": "Chinese",
                        "ar": "Arabic",
                        "hi": "Hindi",
                        "nl": "Dutch",
                        "sv": "Swedish",
                        "pl": "Polish",
                    }.get(code, code.upper()),
                    "voice_count": 0
                }

            languages[code]["voice_count"] += 1

        return {
            "count": len(languages),
            "languages": sorted(
                languages.values(),
                key=lambda x: x["name"]
            )
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Voice listing timed out")

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to retrieve languages")
