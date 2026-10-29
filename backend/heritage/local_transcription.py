"""Private, loopback-only transcription endpoint for the local web application."""
import json
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from whisper_transcription import transcrire_somali, MAX_AUDIO_BYTES

EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".webm"}


def local_post(handler):
    """Handle a local upload without adding a public administrative API."""
    def reply(status, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.send_header("Content-Length", str(len(payload)))
        handler.end_headers()
        handler.wfile.write(payload)

    if urlsplit(handler.path).path != "/api/local/transcrire":
        return reply(404, {"error": "Route inconnue"})
    if handler.client_address[0] not in ("127.0.0.1", "::1"):
        return reply(403, {"error": "Accès local uniquement"})
    host = handler.headers.get("Host", "")
    origin = handler.headers.get("Origin", "")
    if host not in ("127.0.0.1:%s" % handler.server.server_port,
                    "localhost:%s" % handler.server.server_port):
        return reply(403, {"error": "Hôte non autorisé"})
    if origin not in ("http://" + host,):
        return reply(403, {"error": "Origine non autorisée"})
    if handler.headers.get("X-Consentement") != "oui":
        return reply(403, {"error": "Consentement requis"})
    ext = handler.headers.get("X-Audio-Extension", "").lower()
    if ext not in EXTENSIONS:
        return reply(415, {"error": "Format audio non accepté"})
    if handler.headers.get("Content-Type") != "application/octet-stream":
        return reply(415, {"error": "Type de contenu non accepté"})
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        length = 0
    if length <= 0 or length > MAX_AUDIO_BYTES:
        return reply(413, {"error": "Audio vide ou supérieur à 100 Mo"})
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            path = Path(tmp.name)
            remaining = length
            while remaining:
                chunk = handler.rfile.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError("Enregistrement incomplet")
                tmp.write(chunk)
                remaining -= len(chunk)
        result = transcrire_somali(path)
        # Extra lexical metadata is consumed silently by the UI; the transcript is unchanged.
        return reply(200, {
            "texte": result["texte"],
            "segments": result["segments"],
            "mots_somali": result.get("mots_somali", []),
            "moteur": result.get("moteur", "faster-whisper"),
        })
    except Exception:
        return reply(500, {"error": "Transcription impossible. Vérifiez le fichier et l'installation du moteur local."})
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
