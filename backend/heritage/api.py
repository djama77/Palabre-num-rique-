"""Minimal read-only heritage API. Python standard library, no external packages.
Run only behind a properly configured reverse proxy for production.
No administrative or private-content endpoints are exposed.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
from storage import HeritageStorage

DB_PATH = os.environ.get("PALABRE_DB_PATH", str(Path(__file__).parent / "heritage.sqlite3"))
MAX_ID_LENGTH = 100

def public_response(store, path):
    """Pure routing helper for testing; returns (HTTP status, JSON object)."""
    path = urlsplit(path).path
    if path == "/api/health":
        return 200, {"status": "ok"}
    if path == "/api/heritage/public":
        return 200, {"records": store.list_public()}
    prefix = "/api/heritage/public/"
    if path.startswith(prefix):
        record_id = unquote(path[len(prefix):])
        if not record_id or len(record_id) > MAX_ID_LENGTH or "/" in record_id:
            return 400, {"error": "Identifiant invalide"}
        try:
            record = store.get_public(record_id)
        except PermissionError:
            record = None
        return (200, record) if record else (404, {"error": "Récit introuvable"})
    return 404, {"error": "Route inconnue"}

class Handler(BaseHTTPRequestHandler):
    store = None

    def do_GET(self):
        try:
            status, body = public_response(self.store, self.path)
        except Exception:
            status, body = 500, {"error": "Erreur interne"}
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        self.send_error(405, "Écriture non disponible sur cette API")

def serve(host="127.0.0.1", port=8765, db_path=DB_PATH):
    Handler.store = HeritageStorage(db_path)
    server = ThreadingHTTPServer((host, port), Handler)
    print("API publique locale : http://%s:%s" % (host, port))
    server.serve_forever()

if __name__ == "__main__":
    serve(host=os.environ.get("PALABRE_HOST", "127.0.0.1"),
          port=int(os.environ.get("PALABRE_PORT", "8765")))
