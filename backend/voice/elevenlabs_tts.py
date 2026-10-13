"""Optional ElevenLabs speech synthesis for Palabre Numérique.

Designed as a backend-only adapter. Never call this from a public browser.
The original recorded voice of a Sage remains the authoritative archive.
"""
import os
import urllib.error
import urllib.request
import json

MAX_TEXT_CHARS = 1200

class VoiceConfigurationError(RuntimeError):
    pass

def synthesize_validated_text(text: str, *, voice_id: str, approved: bool) -> bytes:
    """Return MP3 bytes. Caller MUST authenticate and authorize the request."""
    if not approved:
        raise PermissionError("Contenu non validé par le Collège des Sages")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_CHARS:
        raise ValueError("Texte requis (1 à 1200 caractères)")
    if not voice_id or not all(c.isalnum() or c in "-_" for c in voice_id):
        raise ValueError("Identifiant de voix invalide")
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise VoiceConfigurationError("ELEVENLABS_API_KEY non configurée")
    model = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
    payload = json.dumps({"text": text, "model_id": model}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            audio = response.read(5_000_001)
            if len(audio) > 5_000_000:
                raise ValueError("Réponse audio trop volumineuse")
            return audio
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Service vocal indisponible (HTTP %s)" % exc.code) from exc
