import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import voicestudio_client as client


class VoiceStudioClientTests(unittest.TestCase):
    def test_remote_http_is_rejected(self):
        with patch.dict(os.environ, {
            "VOICESTUDIO_BASE_URL": "http://192.168.1.20:3900",
            "PALABRE_ALLOW_REMOTE_VOICESTUDIO": "yes"
        }, clear=False):
            with self.assertRaises(client.VoiceStudioError):
                client._config()

    def test_remote_requires_explicit_opt_in_and_https(self):
        with patch.dict(os.environ, {
            "VOICESTUDIO_BASE_URL": "https://voicestudio.example",
        }, clear=False):
            os.environ.pop("PALABRE_ALLOW_REMOTE_VOICESTUDIO", None)
            with self.assertRaises(client.VoiceStudioError):
                client._config()

    def test_synthesis_requires_human_approval(self):
        with self.assertRaises(PermissionError):
            client.synthesize("Texte de test", model="test-model", approved=False)

    def test_synthesis_posts_to_compatible_endpoint(self):
        with patch.dict(os.environ, {"VOICESTUDIO_BASE_URL": "http://127.0.0.1:3900"}, clear=False), \
             patch.object(client, "_request", return_value=b"fake-mp3") as request:
            audio = client.synthesize("Texte validé", model="test-model", approved=True)
        self.assertEqual(audio, b"fake-mp3")
        args = request.call_args.args
        self.assertEqual(args[0], "http://127.0.0.1:3900/v1/audio/speech")
        self.assertIn(b"Texte validÃ©", args[1])

    def test_transcription_validates_extension_before_request(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "notes.txt"
            path.write_text("non audio", encoding="utf-8")
            with patch.object(client, "_request") as request:
                with self.assertRaises(ValueError):
                    client.transcribe(path, model="test-model")
                request.assert_not_called()

    def test_transcription_parses_text_response(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.wav"
            path.write_bytes(b"non-sensitive fixture")
            with patch.dict(os.environ, {"VOICESTUDIO_BASE_URL": "http://127.0.0.1:3900"}, clear=False), \
                 patch.object(client, "_request", return_value=json.dumps({"text": "Tusaale", "language": "so"}).encode()) as request:
                result = client.transcribe(path, model="test-model")
        self.assertEqual(result["text"], "Tusaale")
        self.assertEqual(result["language"], "so")
        self.assertIn("/v1/audio/transcriptions", request.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
