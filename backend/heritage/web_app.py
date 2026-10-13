"""Same-origin local web interface for public, validated heritage records.

Launch: python web_app.py
The UI is read-only and must not be exposed directly to the public internet.
"""
import os
from pathlib import Path
from api import Handler, DB_PATH
from storage import HeritageStorage
from http.server import ThreadingHTTPServer
from local_transcription import local_post
from local_narration import narration_get

UI_FILE = Path(__file__).resolve().parents[2] / "frontend" / "heritage" / "index.html"

class WebHandler(Handler):
    def do_POST(self):
        return local_post(self)

    def do_GET(self):
        if narration_get(self):
            return
        if self.path in ("/", "/index.html"):
            try:
                body = UI_FILE.read_bytes()
            except OSError:
                self.send_error(500, "Interface introuvable")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

def serve(host="127.0.0.1", port=8765, db_path=DB_PATH):
    WebHandler.store = HeritageStorage(db_path)
    if host not in ("127.0.0.1", "::1"):
        raise ValueError("La transcription est réservée au serveur local (127.0.0.1)")
    server = ThreadingHTTPServer((host, port), WebHandler)
    print("Palabre numérique : http://%s:%s/" % (host, port))
    server.serve_forever()

if __name__ == "__main__":
    serve(host=os.environ.get("PALABRE_HOST", "127.0.0.1"),
          port=int(os.environ.get("PALABRE_PORT", "8765")))
