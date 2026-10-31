"""Authenticated HTTP wrapper for Somali faster-whisper transcription."""
from __future__ import annotations
import os, tempfile
from functools import lru_cache
from pathlib import Path
from typing import Annotated
import httpx
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
MODEL_NAME = os.environ.get("WHISPER_MODEL", "small")
DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
MAX_AUDIO_BYTES = int(os.environ.get("MAX_AUDIO_BYTES", str(100 * 1024 * 1024)))
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".webm"}
DEFAULT_ORIGINS = "https://palabre-numerique.vercel.app,https://palabre-numerique-ndnexly2j-diasporajog-7042.vercel.app"
ALLOWED_ORIGINS = [v.strip() for v in os.environ.get("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if v.strip()]
app = FastAPI(title="Palabre Numérique — transcription somalie", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])

@lru_cache(maxsize=1)
def get_model():
    return WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)

async def verify_supabase_token(authorization: str | None):
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503, detail="Authentification Supabase non configurée")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Session Supabase requise")
    token = authorization.split(" ", 1)[1].strip()
    if not token: raise HTTPException(status_code=401, detail="Jeton manquant")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{SUPABASE_URL}/auth/v1/user", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"})
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Service d’authentification indisponible") from exc
    if response.status_code != 200: raise HTTPException(status_code=401, detail="Session Supabase invalide ou expirée")
    user = response.json()
    if not user.get("id"): raise HTTPException(status_code=401, detail="Utilisateur non reconnu")
    return user

@app.get("/health")
async def health():
    return {"status": "ok", "service": "palabre-whisper", "model_loaded": get_model.cache_info().currsize > 0}

@app.post("/api/transcribe")
async def transcribe(file: Annotated[UploadFile, File(...)], authorization: Annotated[str | None, Header()] = None):
    await verify_supabase_token(authorization)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS: raise HTTPException(status_code=415, detail="Format audio non autorisé")
    if file.content_type and not (file.content_type.startswith("audio/") or file.content_type == "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Type de fichier non audio")
    data = await file.read(MAX_AUDIO_BYTES + 1)
    if not data or len(data) > MAX_AUDIO_BYTES: raise HTTPException(status_code=413, detail="Fichier vide ou trop volumineux")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="palabre-", suffix=suffix, delete=False) as temp:
            temp.write(data); temp_path = temp.name
        segments, info = get_model().transcribe(temp_path, language="so", task="transcribe", beam_size=5, vad_filter=True)
        result = []
        for segment in segments:
            phrase = segment.text.strip()
            if phrase: result.append({"debut": round(float(segment.start), 2), "fin": round(float(segment.end), 2), "texte": phrase})
        return {"langue_demandee": "so", "langue_detectee": getattr(info, "language", None), "modele": MODEL_NAME, "segments": result, "texte": " ".join(item["texte"] for item in result)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Échec de la transcription ; vérifiez l’audio et réessayez") from exc
    finally:
        await file.close()
        if temp_path:
            try: os.unlink(temp_path)
            except OSError: pass
