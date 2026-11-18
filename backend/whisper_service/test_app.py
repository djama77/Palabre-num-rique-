"""Focused API tests for the remote Whisper service; no model download required."""
import asyncio
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

import app as whisper_app


class FakeModel:
    def __init__(self):
        self.path_seen = None

    def transcribe(self, path, **kwargs):
        self.path_seen = path
        segments = [
            SimpleNamespace(start=0.12, end=1.34, text="  Tusaale qoraal  "),
            SimpleNamespace(start=1.4, end=2.0, text=""),
        ]
        return iter(segments), SimpleNamespace(language="so")


class WhisperServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(whisper_app.app)
        self.auth = patch.object(
            whisper_app, "verify_supabase_token", new=AsyncMock(return_value={"id": "user-1"})
        )
        self.auth.start()
        self.addCleanup(self.auth.stop)

    def test_health_does_not_load_model(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["model_loaded"])

    def test_transcription_returns_somali_segments_and_deletes_temp_file(self):
        fake = FakeModel()
        with patch.object(whisper_app, "get_model", return_value=fake):
            response = self.client.post(
                "/api/transcribe",
                headers={"Authorization": "Bearer test-token"},
                files={"file": ("sample.wav", b"audio-bytes", "audio/wav")},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["langue_demandee"], "so")
        self.assertEqual(body["langue_detectee"], "so")
        self.assertEqual(body["texte"], "Tusaale qoraal")
        self.assertEqual(body["segments"][0]["debut"], 0.12)
        self.assertIsNotNone(fake.path_seen)
        self.assertFalse(os.path.exists(fake.path_seen))

    def test_unsupported_extension_is_rejected(self):
        response = self.client.post(
            "/api/transcribe",
            headers={"Authorization": "Bearer test-token"},
            files={"file": ("sample.exe", b"not-audio", "application/octet-stream")},
        )
        self.assertEqual(response.status_code, 415)

    def test_non_audio_content_type_is_rejected(self):
        response = self.client.post(
            "/api/transcribe",
            headers={"Authorization": "Bearer test-token"},
            files={"file": ("sample.wav", b"not-audio", "text/plain")},
        )
        self.assertEqual(response.status_code, 415)

    def test_empty_file_is_rejected(self):
        response = self.client.post(
            "/api/transcribe",
            headers={"Authorization": "Bearer test-token"},
            files={"file": ("sample.wav", b"", "audio/wav")},
        )
        self.assertEqual(response.status_code, 413)

    def test_file_over_limit_is_rejected(self):
        with patch.object(whisper_app, "MAX_AUDIO_BYTES", 3):
            response = self.client.post(
                "/api/transcribe",
                headers={"Authorization": "Bearer test-token"},
                files={"file": ("sample.wav", b"four", "audio/wav")},
            )
        self.assertEqual(response.status_code, 413)

    def test_invalid_session_is_rejected(self):
        with patch.object(
            whisper_app,
            "verify_supabase_token",
            new=AsyncMock(side_effect=HTTPException(status_code=401, detail="Session invalide")),
        ):
            response = self.client.post(
                "/api/transcribe",
                headers={"Authorization": "Bearer invalid"},
                files={"file": ("sample.wav", b"audio", "audio/wav")},
            )
        self.assertEqual(response.status_code, 401)

    def test_whisper_failure_returns_generic_error_and_cleans_temp_file(self):
        class BrokenModel:
            path_seen = None

            def transcribe(self, path, **kwargs):
                self.path_seen = path
                raise RuntimeError("internal detail must not leak")

        fake = BrokenModel()
        with patch.object(whisper_app, "get_model", return_value=fake):
            response = self.client.post(
                "/api/transcribe",
                headers={"Authorization": "Bearer test-token"},
                files={"file": ("sample.wav", b"audio", "audio/wav")},
            )
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("internal detail", response.text)
        self.assertFalse(os.path.exists(fake.path_seen))


if __name__ == "__main__":
    unittest.main()
