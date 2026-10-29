import os
import tempfile
import unittest
from pathlib import Path

from storage import HeritageStorage
from local_archive import create_local_archive
from workflow import Status


class LocalArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = HeritageStorage(self.root / "heritage.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def test_saves_audio_and_draft_metadata(self):
        result = create_local_archive(
            self.store, "Sheeko tijaabo", b"fake-audio-bytes", ".webm", True,
            "Qoraal somali ah"
        )
        record = self.store.get(result["id"])
        self.assertEqual(record.title_so, "Sheeko tijaabo")
        self.assertEqual(record.status, Status.DRAFT)
        self.assertEqual(record.transcript_so, "Qoraal somali ah")
        self.assertTrue(record.consent_recorded)
        audio_path = self.root / record.original_audio_path
        self.assertEqual(audio_path.read_bytes(), b"fake-audio-bytes")
        self.assertFalse(result["transcript_saved"] is False)

    def test_rejects_missing_consent(self):
        with self.assertRaises(PermissionError):
            create_local_archive(self.store, "Sheeko", b"audio", ".wav", False)

    def test_rejects_invalid_extension(self):
        with self.assertRaises(ValueError):
            create_local_archive(self.store, "Sheeko", b"audio", ".exe", True)

    def test_rejects_empty_title_or_audio(self):
        with self.assertRaises(ValueError):
            create_local_archive(self.store, "", b"audio", ".wav", True)
        with self.assertRaises(ValueError):
            create_local_archive(self.store, "Sheeko", b"", ".wav", True)


if __name__ == "__main__":
    unittest.main()
