"""Loopback-only read endpoint for local Xeer-Yaqaan evidence search."""
import json
from pathlib import Path
from urllib.parse import urlsplit

from xeer_yaqaan import search_evidence

CORPUS = Path(__file__).resolve().parents[2] / "data" / "xeer-cisse" / "ocr" / "xeer-cisse.txt"
MAX_BODY_BYTES = 10 * 1024


def local_xeer_post(handler):
    def reply(status, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.send_header("Content-Length", str(len(payload)))
        handler.end_headers()
        handler.wfile.write(payload)

    if urlsplit(handler.path).path != "/api/local/xeer-search":
        return reply(404, {"error": "Route inconnue"})
    if handler.client_address[0] not in ("127.0.0.1", "::1"):
        return reply(403, {"error": "Accès local uniquement"})
    host = handler.headers.get("Host", "")
    origin = handler.headers.get("Origin", "")
    if host not in (
        "127.0.0.1:%s" % handler.server.server_port,
        "localhost:%s" % handler.server.server_port,
        "[::1]:%s" % handler.server.server_port,
    ):
        return reply(403, {"error": "Hôte non autorisé"})
    if origin not in ("http://" + host,):
        return reply(403, {"error": "Origine non autorisée"})
    if handler.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
        return reply(415, {"error": "Type de contenu non accepté"})
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        length = 0
    if length <= 0 or length > MAX_BODY_BYTES:
        return reply(413, {"error": "Requête vide ou trop volumineuse"})
    try:
        raw = handler.rfile.read(length)
        payload = json.loads(raw.decode("utf-8"))
        question = payload.get("question", "") if isinstance(payload, dict) else ""
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            return reply(400, {"error": "Saisissez une question de 1 à 1000 caractères."})
        if not CORPUS.is_file():
            return reply(503, {
                "error": "Le corpus OCR est absent. Préparez-le avec backend/heritage/prepare_xeer_pdf.py."
            })
        return reply(200, search_evidence(question, CORPUS, limit=5))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return reply(400, {"error": "JSON invalide."})
    except ValueError as exc:
        return reply(400, {"error": str(exc)})
    except Exception:
        return reply(500, {"error": "Recherche impossible. Vérifiez le corpus OCR."})
