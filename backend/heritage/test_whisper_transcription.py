import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from workflow import HeritageRecord, Status
from whisper_transcription import validate_audio, transcrire_brouillon

class WhisperTests(unittest.TestCase):
    def test_invalid_extension(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "sample.exe"
            p.write_bytes(b"bad")
            with self.assertRaises(ValueError):
                validate_audio(p)

    def test_empty_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "sample.wav"
            p.write_bytes(b"")
            with self.assertRaises(ValueError):
                validate_audio(p)

    def test_requires_consent(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "sample.wav"
            p.write_bytes(b"test")
            record = HeritageRecord("1", "Sheeko", "sample.wav", False)
            with self.assertRaises(PermissionError):
                transcrire_brouillon(record, actor="collector", audio_root=folder)

    def test_transcription_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "sample.wav"
            p.write_bytes(b"test")
            record = HeritageRecord("1", "Sheeko", "sample.wav", True)
            result = {"texte":"Tani waa sheeko", "segments":[], "langue_demandee":"so"}
            with patch("whisper_transcription.transcrire_somali", return_value=result):
                output = transcrire_brouillon(record, actor="collector", audio_root=folder)
            self.assertEqual(output["texte"], "Tani waa sheeko")
            self.assertEqual(record.status, Status.TRANSCRIBED)
            self.assertEqual(record.access_level, "restricted")
            with self.assertRaises(PermissionError):
                record.public_payload()

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "protected"
            root.mkdir()
            outside = Path(folder) / "outside.wav"
            outside.write_bytes(b"test")
            record = HeritageRecord("1", "Sheeko", "../outside.wav", True)
            with self.assertRaises(PermissionError):
                transcrire_brouillon(record, actor="collector", audio_root=root)

if __name__ == "__main__":
    unittest.main()
