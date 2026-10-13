"""Offline Somali speech transcription using faster-whisper.

Install optional dependency: python -m pip install faster-whisper
Models download on first use. No recording is sent to a remote API.
This module never approves or publishes heritage records.
"""
from pathlib import Path

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus"}
MAX_AUDIO_BYTES = 100 * 1024 * 1024

def validate_audio(path):
    audio = Path(path).expanduser().resolve(strict=True)
    if not audio.is_file():
        raise ValueError("Le chemin ne désigne pas un fichier audio")
    if audio.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Format audio non autorisé")
    if audio.stat().st_size == 0 or audio.stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError("Taille audio non autorisée (maximum 100 Mo)")
    return audio

def transcrire_somali(audio_path, *, model_name="small", device="cpu",
                      compute_type="int8"):
    """Return timestamped segments, detected language and Somali text.

    Caller must establish informed consent, access authorization, and
    verify the audio belongs to the requested heritage record.
    """
    audio = validate_audio(audio_path)
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Installer faster-whisper : python -m pip install faster-whisper"
        ) from exc
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        str(audio), language="so", task="transcribe", beam_size=5,
        vad_filter=True
    )
    result = []
    for segment in segments:
        text = segment.text.strip()
        if text:
            result.append({
                "debut": round(float(segment.start), 2),
                "fin": round(float(segment.end), 2),
                "texte": text
            })
    return {
        "langue_demandee": "so",
        "langue_detectee": getattr(info, "language", None),
        "modele": model_name,
        "segments": result,
        "texte": " ".join(part["texte"] for part in result)
    }

def transcrire_brouillon(record, *, actor, audio_root, model_name="small"):
    """Transcribe a consenting draft whose audio is within a protected directory.

    This is a local trusted-backend helper, not an unauthenticated HTTP route.
    The caller must authenticate/authorize actor. Human review is mandatory.
    """
    from workflow import Status
    if record.status != Status.DRAFT:
        raise ValueError("Seuls les brouillons peuvent être transcrits")
    if not record.consent_recorded:
        raise PermissionError("Consentement requis avant transcription")
    if not actor:
        raise PermissionError("Opérateur authentifié requis")
    root = Path(audio_root).expanduser().resolve(strict=True)
    path = (root / record.original_audio_path).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise PermissionError("Audio hors du répertoire autorisé")
    result = transcrire_somali(path, model_name=model_name)
    if not result["texte"]:
        raise ValueError("Aucune parole transcrite ; examen manuel requis")
    record.attach_transcription(result["texte"], actor)
    return result
