"""Compare Somali ASR engines on one local audio file, without uploading it.

Example (PowerShell):
  python scripts/evaluate_somali_asr.py --audio "C:\\audio\\extrait.wav" \
    --reference "C:\\audio\\extrait-reference.txt" \
    --ogaal-model "C:\\Models\\Ogaal-ASR" \
    --whisper-model "C:\\Models\\faster-whisper-small"

The reference file must contain a human-verified Somali transcript. The script
writes only text metrics to the requested report; audio remains in place.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
HERITAGE = ROOT / "backend" / "heritage"
if str(HERITAGE) not in sys.path:
    sys.path.insert(0, str(HERITAGE))

from whisper_transcription import transcrire_somali  # noqa: E402


def normalize(text: str) -> list[str]:
    """Normalize punctuation/case for comparable word error rate."""
    return re.findall(r"[^\W_]+(?:[-'][^\W_]+)*", text.casefold(), flags=re.UNICODE)


def edit_distance(reference: Iterable[str], hypothesis: Iterable[str]) -> int:
    """Levenshtein distance using linear memory."""
    ref, hyp = list(reference), list(hypothesis)
    previous = list(range(len(hyp) + 1))
    for i, left in enumerate(ref, 1):
        current = [i]
        for j, right in enumerate(hyp, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (left != right),
            ))
        previous = current
    return previous[-1]


def error_rate(reference: str, hypothesis: str, *, characters: bool = False) -> float:
    if characters:
        ref_units = list("".join(normalize(reference)))
        hyp_units = list("".join(normalize(hypothesis)))
    else:
        ref_units = normalize(reference)
        hyp_units = normalize(hypothesis)
    if not ref_units:
        raise ValueError("La transcription de référence est vide.")
    return edit_distance(ref_units, hyp_units) / len(ref_units)


def run_one(engine: str, audio: Path, *, whisper_model: Path, ogaal_model: Path) -> dict:
    os.environ["PALABRE_OGAAL_MODEL_DIR"] = str(ogaal_model)
    started = time.perf_counter()
    if engine == "ogaal":
        result = transcrire_somali(audio, engine="ogaal")
    else:
        # A local directory is required: no model-name lookup or download.
        if not whisper_model.is_dir():
            raise ValueError(f"Répertoire faster-whisper local introuvable : {whisper_model}")
        result = transcrire_somali(audio, engine="whisper", model_name=str(whisper_model))
    return {
        "engine": engine,
        "seconds": round(time.perf_counter() - started, 2),
        "text": result["texte"],
        "somali_terms": result.get("mots_somali", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, type=Path, help="Fichier audio local")
    parser.add_argument("--reference", required=True, type=Path, help="Texte somali relu par une personne")
    parser.add_argument("--ogaal-model", required=True, type=Path, help="Dossier local du modèle Ogaal-ASR")
    parser.add_argument("--whisper-model", required=True, type=Path, help="Dossier local du modèle CTranslate2 faster-whisper")
    parser.add_argument("--report", type=Path, default=Path("asr-comparison-report.json"), help="Rapport JSON local")
    args = parser.parse_args()

    if not args.audio.is_file():
        parser.error("Le fichier audio local est introuvable.")
    if not args.reference.is_file():
        parser.error("Le fichier de référence local est introuvable.")
    if not args.ogaal_model.is_dir():
        parser.error("Le dossier local du modèle Ogaal-ASR est introuvable.")
    if not args.whisper_model.is_dir():
        parser.error("Le dossier local du modèle faster-whisper est introuvable.")

    reference = args.reference.read_text(encoding="utf-8").strip()
    if not reference:
        parser.error("Le fichier de référence ne doit pas être vide.")

    results = []
    for engine in ("whisper", "ogaal"):
        try:
            item = run_one(
                engine, args.audio,
                whisper_model=args.whisper_model,
                ogaal_model=args.ogaal_model,
            )
            item["wer"] = round(error_rate(reference, item["text"]) * 100, 2)
            item["cer"] = round(error_rate(reference, item["text"], characters=True) * 100, 2)
            results.append(item)
        except Exception as exc:
            results.append({"engine": engine, "error": f"{type(exc).__name__}: {exc}"})

    report = {
        "audio_filename": args.audio.name,
        "reference_filename": args.reference.name,
        "note": "Calcul local. Le rapport ne contient pas l'audio ni la transcription de référence.",
        "results": results,
    }
    args.report.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in results:
        if "error" in item:
            print(f"{item['engine']}: ERREUR — {item['error']}")
        else:
            print(f"{item['engine']}: WER={item['wer']}% | CER={item['cer']}% | durée={item['seconds']} s")
    print(f"Rapport local : {args.report.resolve()}")
    if any("error" in item for item in results):
        return 1
    better = min(results, key=lambda item: item["wer"])
    print(f"Meilleur WER sur cet extrait : {better['engine']} (un seul extrait ne suffit pas pour conclure).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
