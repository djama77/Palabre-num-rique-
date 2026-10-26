"""Optional client for a separately running VoiceStudio local API.

The API contract is based on VoiceStudio's OpenAI-compatible endpoints:
POST /v1/audio/transcriptions and POST /v1/audio/speech.
Keep the API key server-side. Default target is loopback only. Remote hosts
require an explicit opt-in environment variable and HTTPS.
"""
from __future__ import annotations

import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "http://127.0.0.1:3900"
MAX_AUDIO_BYTES = 100 * 1024 * 1024
MAX_TEXT_CHARS = 1200


class VoiceStudioError(RuntimeError):
    pass


def _config():
    base = os.environ.get("VOICESTUDIO_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    parsed = urllib.parse.urlsplit(base)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise VoiceStudioError("URL VoiceStudio invalide")
    is_loopback = parsed.hostname in ("127.0.0.1", "localhost", "::1")
    if not is_loopback and parsed.scheme != "https":
        raise VoiceStudioError("VoiceStudio distant exige HTTPS")
    if not is_loopback and os.environ.get("PALABRE_ALLOW_REMOTE_VOICESTUDIO") != "yes":
        raise VoiceStudioError("VoiceStudio distant non autorisé explicitement")
    return base, os.environ.get("VOICESTUDIO_API_KEY", "")


def _request(url, data, headers, timeout=120):
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(10_000_001)
    except urllib.error.HTTPError as exc:
        raise VoiceStudioError("VoiceStudio a refusé la requête (HTTP %s)" % exc.code) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise VoiceStudioError("VoiceStudio est indisponible ou a dépassé le délai") from exc


def transcribe(audio_path: Path, *, model: str, language: str = "so") -> dict:
    """Transcribe a non-sensitive audio file using VoiceStudio's STT endpoint."""
    path = Path(audio_path).resolve(strict=True)
    if not path.is_file() or path.suffix.lower() not in {
        ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus"
    }:
        raise ValueError("Fichier audio non valide")
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError("Taille audio invalide (maximum 100 Mo)")
    if not model or len(model) > 200:
        raise ValueError("Identifiant de modèle requis")
    base, key = _config()
    boundary = "----PalabreVoiceStudio" + secrets.token_hex(16)
    chunks = []

    def field(name, value):
        chunks.extend([
            ("--" + boundary + "\r\n").encode(),
            ('Content-Disposition: form-data; name="%s"\r\n\r\n' % name).encode(),
            str(value).encode("utf-8"), b"\r\n"
        ])

    field("model", model)
    field("language", language)
    field("response_format", "json")
    chunks.extend([
        ("--" + boundary + "\r\n").encode(),
        ('Content-Disposition: form-data; name="file"; filename="%s"\r\n' % path.name).encode(),
        ("Content-Type: application/octet-stream\r\n\r\n").encode(),
        path.read_bytes(), b"\r\n",
        ("--" + boundary + "--\r\n").encode()
    ])
    headers = {"Content-Type": "multipart/form-data; boundary=" + boundary,
               "Accept": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    raw = _request(base + "/v1/audio/transcriptions", b"".join(chunks), headers)
    if len(raw) > 10_000_000:
        raise VoiceStudioError("Réponse de transcription trop volumineuse")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VoiceStudioError("Réponse de transcription illisible") from exc
    text = result.get("text")
    if not isinstance(text, str):
        raise VoiceStudioError("Réponse sans champ texte")
    return {"text": text, "language": result.get("language", language),
            "segments": result.get("segments", []),
            "engine": result.get("engine", model)}


def synthesize(text: str, *, model: str, voice: str = "alloy",
               approved: bool = False) -> bytes:
    """Generate speech only for text explicitly approved by PALABRE workflow."""
    if not approved:
        raise PermissionError("Validation humaine requise avant narration")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_CHARS:
        raise ValueError("Texte requis (1 à 1200 caractères)")
    if not model or len(model) > 200 or not voice or len(voice) > 200:
        raise ValueError("Modèle et voix requis")
    base, key = _config()
    body = json.dumps({"model": model, "voice": voice, "input": text,
                       "response_format": "mp3"}, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "audio/mpeg"}
    if key:
        headers["Authorization"] = "Bearer " + key
    audio = _request(base + "/v1/audio/speech", body, headers)
    if not audio or len(audio) > 10_000_000:
        raise VoiceStudioError("Réponse audio vide ou trop volumineuse")
    return audio
