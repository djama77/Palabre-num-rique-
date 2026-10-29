import io
import json
import unittest
from unittest.mock import Mock, patch
from local_transcription import local_post


class LocalTranscriptionTests(unittest.TestCase):
    def handler(self, *, path="/api/local/transcrire", origin="http://127.0.0.1:8765",
                consent="oui", client="127.0.0.1", extension=".wav"):
        h = Mock()
        h.path = path
        h.client_address = (client, 1000)
        h.server.server_port = 8765
        h.headers = {
            "Host": "127.0.0.1:8765",
            "Origin": origin,
            "X-Consentement": consent,
            "X-Audio-Extension": extension,
            "Content-Type": "application/octet-stream",
            "Content-Length": "4",
        }
        h.wfile = io.BytesIO()
        h.rfile = io.BytesIO(b"test")
        return h

    def test_reject_remote_client(self):
        h = self.handler(client="192.168.1.5")
        local_post(h)
        h.send_response.assert_called_with(403)

    def test_reject_missing_consent(self):
        h = self.handler(consent="non")
        local_post(h)
        h.send_response.assert_called_with(403)

    def test_reject_cross_origin(self):
        h = self.handler(origin="https://example.com")
        local_post(h)
        h.send_response.assert_called_with(403)

    def test_reject_unknown_route(self):
        h = self.handler(path="/api/local/other")
        local_post(h)
        h.send_response.assert_called_with(404)

    def test_reject_oversize(self):
        h = self.handler()
        h.headers["Content-Length"] = str(101 * 1024 * 1024)
        local_post(h)
        h.send_response.assert_called_with(413)

    def test_webm_upload_returns_silent_somali_metadata(self):
        h = self.handler(extension=".webm")
        result = {
            "texte": "Tani waa sheeko",
            "segments": [],
            "mots_somali": ["sheeko"],
            "moteur": "ogaal",
        }
        with patch("local_transcription.transcrire_somali", return_value=result):
            local_post(h)
        h.send_response.assert_called_with(200)
        payload = json.loads(h.wfile.getvalue().decode("utf-8"))
        self.assertEqual(payload["texte"], "Tani waa sheeko")
        self.assertEqual(payload["mots_somali"], ["sheeko"])
        self.assertEqual(payload["moteur"], "ogaal")


if __name__ == "__main__":
    unittest.main()
