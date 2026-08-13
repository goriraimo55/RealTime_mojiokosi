"""Local faster-whisper bridge for the browser application."""

import argparse
import os
import tempfile
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from starlette.concurrency import run_in_threadpool


parser = argparse.ArgumentParser(description="Run local faster-whisper transcription")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
parser.add_argument("--compute-type", default="default")
args, _ = parser.parse_known_args()

app = FastAPI(title="RealTime local faster-whisper")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def allow_local_network_requests(request, call_next):
    """Allow Chromium pages to reach this loopback service after PNA preflight."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

SUPPORTED_MODELS = {"tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"}


@lru_cache(maxsize=2)
def get_model(name: str) -> WhisperModel:
    """Load models lazily and retain recently selected models."""
    return WhisperModel(name, device=args.device, compute_type=args.compute_type)


def transcribe_file(path: str, model: str, language: Optional[str]) -> str:
    segments, _ = get_model(model).transcribe(
        path,
        language=language or None,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return "".join(segment.text for segment in segments).strip()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form("small"),
    language: Optional[str] = Form(None),
    response_format: str = Form("json"),
) -> dict[str, str]:
    del response_format  # The browser currently consumes JSON only.
    if model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail="Unsupported model")
    suffix = os.path.splitext(file.filename or "chunk.webm")[1] or ".webm"
    path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as audio:
            path = audio.name
            while chunk := await file.read(1024 * 1024):
                audio.write(chunk)
        text = await run_in_threadpool(transcribe_file, path, model, language)
        return {"text": text}
    finally:
        await file.close()
        if path:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)
