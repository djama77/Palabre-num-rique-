"""Create page-labelled OCR text from a scanned Xeer-Ciise PDF.

Requires the command-line tools ocrmypdf and pdftotext. The original PDF is
read-only; OCR output is temporary. Review every page against the original
scan, especially Somali names and customary-law terms.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def prepare_pdf(pdf_path: str | Path, output_path: str | Path, *, language: str = "eng") -> Path:
    source = Path(pdf_path).expanduser().resolve(strict=True)
    destination = Path(output_path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise ValueError("Le fichier source doit être un PDF existant.")
    if source == destination:
        raise ValueError("Le fichier texte de sortie doit être différent du PDF source.")
    for executable in ("ocrmypdf", "pdftotext"):
        if shutil.which(executable) is None:
            raise RuntimeError(
                f"Outil manquant : {executable}. Installez OCRmyPDF et Poppler, puis réessayez."
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="palabre-xeer-") as temporary:
        ocr_pdf = Path(temporary) / "ocr.pdf"
        command = [
            "ocrmypdf", "--skip-text", "--deskew", "--rotate-pages",
            "-l", language, str(source), str(ocr_pdf)
        ]
        subprocess.run(command, check=True)
        extracted = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(ocr_pdf), "-"],
            check=True, capture_output=True, text=True, encoding="utf-8"
        ).stdout
    pages = extracted.split("\f")
    while pages and not pages[-1].strip():
        pages.pop()
    output = []
    for page_number, page in enumerate(pages, start=1):
        cleaned = re.sub(r"\r\n?", "\n", page).strip()
        output.append(f"[[PAGE {page_number}]]\n{cleaned}")
    destination.write_text("\n\n".join(output) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Chemin du PDF original (non modifié)")
    parser.add_argument("output", help="Chemin du fichier texte OCR à créer")
    parser.add_argument(
        "--language", default="eng",
        help="Langue Tesseract installée, par ex. eng ou som si le modèle existe (défaut : eng)"
    )
    args = parser.parse_args()
    result = prepare_pdf(args.pdf, args.output, language=args.language)
    print(f"Texte OCR créé : {result}")
    print("IMPORTANT : vérifier les pages et les termes somalis avec le PDF original.")


if __name__ == "__main__":
    main()
