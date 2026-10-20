"""Smoke tests for local web UI without external dependencies."""
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from web_app import WebHandler, UI_FILE
from storage import HeritageStorage
import tempfile

class WebAppTests(unittest.TestCase):
    def test_html_exists_and_contains_controls(self):
        html = UI_FILE.read_text(encoding="utf-8")
        for marker in ('id="search"', 'id="records"', 'id="refresh"', 'speechSynthesis', 'supabase-cloud.js'):
            self.assertIn(marker, html)

    def test_supabase_library_uses_published_records_only(self):
        cloud_script = (UI_FILE.parent / "supabase-cloud.js").read_text(encoding="utf-8")
        for marker in ('palabrePublicLibrary', '.eq("status","published")', '.eq("publication_authorized",true)'):
            self.assertIn(marker, cloud_script)

    def test_local_http_and_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            class TestHandler(WebHandler):
                store = HeritageStorage(str(Path(tmp) / "test.sqlite3"))
                def log_message(self, *args):
                    pass
            server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = "http://127.0.0.1:%d" % server.server_port
                with urlopen(base + "/", timeout=3) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn(b"Palabre", response.read())
                with urlopen(base + "/api/heritage/public", timeout=3) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn(b'"records": []', response.read())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

if __name__ == "__main__":
    unittest.main()
