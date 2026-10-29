import os
import tempfile
import unittest
from pathlib import Path

from storage import HeritageStorage
from local_archive import _multipart_fields, create_local_archive
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
        self.assertTrue(result["transcript_saved"])


    def test_multipart_parser_reads_metadata_and_audio(self):
        boundary = "----palabre-test-boundary"
        body = (
            f"--{boundary}\\r\\nContent-Disposition: form-data; name=\\"title\\"\\r\\n\\r\\nSheeko\\r\\n"
            f"--{boundary}\\r\\nContent-Disposition: form-data; name=\\"transcript\\"\\r\\n\\r\\nQoraal\\r\\n"
            f"--{boundary}\\r\\nContent-Disposition: form-data; name=\\"audio\\"; filename=\\"voix.webm\\"\\r\\n"
            "Content-Type: audio/webm\\r\\n\\r\\nAUDIO_BYTES\\r\\n"
            f"--{boundary}--\\r\\n"
        ).encode()
        fields = _multipart_fields("multipart/form-data; boundary=" + boundary, body)
        self.assertEqual(fields["title"]["value"], "Sheeko")
        self.assertEqual(fields["transcript"]["value"], "Qoraal")
        self.assertEqual(fields["audio"]["filename"], "voix.webm")
        self.assertEqual(fields["audio"]["value"], b"AUDIO_BYTES")

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
