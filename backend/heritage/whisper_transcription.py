"""Offline Somali speech transcription with local lexical hints and optional Ogaal-ASR.

No recording is sent to a remote API. Models must already be installed locally.
Transcription never approves or publishes heritage records.
"""
import os
from functools import lru_cache
from pathlib import Path

from somali_lexicon import enrich_result, vocabulary_prompt

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".webm"}
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


def _ogaal_model_dir():
    configured = os.environ.get("PALABRE_OGAAL_MODEL_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path(__file__).resolve().parents[2] / "models" / "ogaal-asr"


@lru_cache(maxsize=2)
def _load_ogaal_pipeline(model_dir_text):
    """Load and cache a local model so each upload does not reload large weights."""
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Ogaal-ASR requiert Transformers et PyTorch installés localement."
        ) from exc
    model_dir = Path(model_dir_text)
    return pipeline(
        "automatic-speech-recognition",
        model=str(model_dir),
        tokenizer=str(model_dir),
        feature_extractor=str(model_dir),
        device=-1,
        model_kwargs={"local_files_only": True},
    )


def _transcribe_ogaal(audio):
    """Run Ogaal-ASR from an already downloaded local model directory only."""
    model_dir = _ogaal_model_dir()
    if not model_dir.is_dir():
        raise RuntimeError(
            "Modèle Ogaal local introuvable. Définissez PALABRE_OGAAL_MODEL_DIR "
            "ou utilisez PALABRE_ASR_ENGINE=whisper."
        )
    asr = _load_ogaal_pipeline(str(model_dir.resolve()))
    prediction = asr(str(audio))
    text = str(prediction.get("text", "")).strip()
    return {
        "langue_demandee": "so",
        "langue_detectee": "so",
        "modele": "Ogaal-ASR-local",
        "moteur": "ogaal",
        "segments": [],
        "texte": text,
    }


def transcrire_somali(audio_path, *, model_name="small", device="cpu",
                      compute_type="int8", engine=None):
    """Return Somali text, optional timestamps and lexicon-only annotations.

    engine: auto (default), whisper, or ogaal. Auto selects Ogaal only when its
    model directory is already available locally; it never downloads it.
    """
    audio = validate_audio(audio_path)
    selected_engine = (engine or os.environ.get("PALABRE_ASR_ENGINE", "auto")).lower()
    if selected_engine not in {"auto", "whisper", "ogaal"}:
        raise ValueError("Moteur inconnu : utilisez auto, whisper ou ogaal")
    oga_dir = _ogaal_model_dir()
    if selected_engine == "ogaal" or (selected_engine == "auto" and oga_dir.is_dir()):
        return enrich_result(_transcribe_ogaal(audio))
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Installer faster-whisper : python -m pip install -r requirements-whisper.txt"
        ) from exc
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        str(audio), language="so", task="transcribe", beam_size=5,
        vad_filter=True, initial_prompt=vocabulary_prompt()
    )
    result_segments = []
    for segment in segments:
        text = segment.text.strip()
        if text:
            result_segments.append({
                "debut": round(float(segment.start), 2),
                "fin": round(float(segment.end), 2),
                "texte": text
            })
    result = {
        "langue_demandee": "so",
        "langue_detectee": getattr(info, "language", None),
        "modele": model_name,
        "moteur": "faster-whisper",
        "segments": result_segments,
        "texte": " ".join(part["texte"] for part in result_segments)
    }
    return enrich_result(result)


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
