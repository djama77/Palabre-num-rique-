import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audio_providers import FasterWhisperProvider, sha256_file


class AudioProviderTests(unittest.TestCase):
    def test_sha256_does_not_modify_original(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.wav"
            original = b"non-sensitive prototype fixture"
            path.write_bytes(original)
            before = path.read_bytes()
            self.assertEqual(sha256_file(path), hashlib.sha256(original).hexdigest())
            self.assertEqual(path.read_bytes(), before)

    @patch("whisper_transcription.transcrire_somali")
    def test_faster_whisper_adapter_maps_result(self, mock_transcribe):
        mock_transcribe.return_value = {
            "texte": "Tusaale qoraal",
            "segments": [{"debut": 0.0, "fin": 1.2, "texte": "Tusaale qoraal"}],
            "langue_demandee": "so",
            "langue_detectee": "so",
            "modele": "tiny",
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.wav"
            path.write_bytes(b"fixture")
            provider = FasterWhisperProvider(model_name="tiny")
            result = provider.transcribe(path)
        self.assertEqual(result.text, "Tusaale qoraal")
        self.assertEqual(result.language_requested, "so")
        self.assertEqual(result.engine, "faster-whisper:tiny")
        mock_transcribe.assert_called_once()

    def test_invalid_file_is_rejected_by_underlying_engine(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.txt"
            path.write_text("not audio", encoding="utf-8")
            provider = FasterWhisperProvider(model_name="tiny")
            with self.assertRaises(ValueError):
                provider.transcribe(path)


if __name__ == "__main__":
    unittest.main()
