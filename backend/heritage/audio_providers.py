"""Provider boundary for PALABRE NUMÉRIQUE audio processing.

Keeps heritage workflow and authorization in PALABRE; audio engines are replaceable.
This module does not assume undocumented VoiceStudio API routes. VoiceStudio can
only be wired in after its installed version's local API contract is verified.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Any


@dataclass
class TranscriptionResult:
    text: str
    segments: list[dict[str, Any]]
    language_requested: str
    language_detected: str | None
    engine: str


class TranscriptionProvider(Protocol):
    def transcribe(self, audio_path: Path) -> TranscriptionResult: ...


class NarrationProvider(Protocol):
    def synthesize(self, text: str, *, approved: bool) -> bytes: ...


class FasterWhisperProvider:
    """Adapter over the existing local Somali transcription module."""

    def __init__(self, model_name: str = "small", device: str = "cpu",
                 compute_type: str = "int8"):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        # Import lazily so the base application works without optional ML packages.
        from whisper_transcription import transcrire_somali
        result = transcrire_somali(
            audio_path, model_name=self.model_name, device=self.device,
            compute_type=self.compute_type
        )
        return TranscriptionResult(
            text=result["texte"],
            segments=result["segments"],
            language_requested=result["langue_demandee"],
            language_detected=result.get("langue_detectee"),
            engine=f"faster-whisper:{self.model_name}",
        )


class BrowserNarrationNote:
    """Marker for the existing browser SpeechSynthesis fallback.

    Actual browser speech stays in frontend/modules/heritage-audio.js; this
    backend class intentionally does not imitate browser capabilities.
    """
    name = "browser-speech-synthesis"


class ElevenLabsNarrationProvider:
    """Adapter over the existing backend-only ElevenLabs function."""

    def __init__(self, voice_id: str):
        self.voice_id = voice_id

    def synthesize(self, text: str, *, approved: bool) -> bytes:
        from elevenlabs_tts import synthesize_validated_text
        return synthesize_validated_text(
            text, voice_id=self.voice_id, approved=approved
        )


def sha256_file(path: Path) -> str:
    """Fingerprint an original audio file without modifying it."""
    import hashlib
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
