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
        crlf = "\r\n"
        body = (
            f'--{boundary}{crlf}Content-Disposition: form-data; name="title"{crlf}{crlf}Sheeko{crlf}'
            f'--{boundary}{crlf}Content-Disposition: form-data; name="transcript"{crlf}{crlf}Qoraal{crlf}'
            f'--{boundary}{crlf}Content-Disposition: form-data; name="audio"; filename="voix.webm"{crlf}'
            f'Content-Type: audio/webm{crlf}{crlf}AUDIO_BYTES{crlf}'
            f'--{boundary}--{crlf}'
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
