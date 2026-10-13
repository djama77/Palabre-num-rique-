"""Local narration of already published French translations.

Only published database text is sent to ElevenLabs, never arbitrary browser text.
No Sages validation requirement. The existing explicit publication authorization
and consent checks apply through the record's public_payload().
"""
import os
from urllib.parse import urlsplit, unquote
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "voice"))
from elevenlabs_tts import synthesize_validated_text, VoiceConfigurationError

PREFIX = "/api/local/ecouter/"
def narration_get(handler):
    if not urlsplit(handler.path).path.startswith(PREFIX):
        return False
    def error(code, message):
        handler.send_error(code, message)
    host = handler.headers.get("Host", "")
    if handler.client_address[0] not in ("127.0.0.1", "::1") or host not in (
        f"localhost:{handler.server.server_port}", f"127.0.0.1:{handler.server.server_port}"
    ):
        error(403, "Accès local uniquement")
        return True
    record_id = unquote(urlsplit(handler.path).path[len(PREFIX):])
    if not record_id or len(record_id) > 100 or "/" in record_id:
        error(400, "Identifiant invalide")
        return True
    try:
        record = handler.store.get_public(record_id)
    except PermissionError:
        record = None
    if not record or not record.get("translation_fr", "").strip():
        error(404, "Traduction publique introuvable")
        return True
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "")
    if not voice_id:
        error(503, "Voix non configurée")
        return True
    try:
        audio = synthesize_validated_text(
            record["translation_fr"], voice_id=voice_id, approved=True
        )
    except (VoiceConfigurationError, ValueError, RuntimeError, PermissionError):
        error(503, "Narration indisponible")
        return True
    handler.send_response(200)
    handler.send_header("Content-Type", "audio/mpeg")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(audio)))
    handler.end_headers()
    handler.wfile.write(audio)
    return True
