import os
import tempfile
import unittest
from storage import HeritageStorage
from workflow import HeritageRecord


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = HeritageStorage(os.path.join(self.temp.name, "heritage.sqlite3"))

    def tearDown(self):
        self.temp.cleanup()

    def test_roundtrip_private(self):
        record = HeritageRecord("r1", "Sheeko", "private/audio.wav", True, collector_id="collector")
        self.store.save(record)
        result = self.store.get("r1")
        self.assertEqual(result.title_so, "Sheeko")
        self.assertEqual(result.collector_id, "collector")
        with self.assertRaises(PermissionError):
            self.store.get_public("r1")
        self.assertEqual(self.store.list_public(), [])

    def test_published_public(self):
        record = HeritageRecord("r2", "Sheeko", "private/audio.wav", True, collector_id="collector")
        record.attach_transcription("Qoraal", "transcriber")
        record.translation_fr = "Récit traduit"
        record.validate_by_sage("sage-1", role="sage")
        record.publish("publisher", publication_authorized=True)
        self.store.save(record)
        public = self.store.get_public("r2")
        self.assertEqual(public["translation_fr"], "Récit traduit")
        self.assertNotIn("original_audio_path", public)
        self.assertNotIn("collector_id", public)
        self.assertEqual(len(self.store.list_public()), 1)

    def test_legacy_database_is_migrated(self):
        legacy_path = os.path.join(self.temp.name, "legacy.sqlite3")
        import sqlite3
        db = sqlite3.connect(legacy_path)
        db.execute("""CREATE TABLE heritage_records (
            id TEXT PRIMARY KEY, title_so TEXT NOT NULL, original_audio_path TEXT NOT NULL,
            consent_recorded INTEGER NOT NULL, status TEXT NOT NULL,
            transcript_so TEXT NOT NULL DEFAULT '', translation_fr TEXT NOT NULL DEFAULT '',
            access_level TEXT NOT NULL DEFAULT 'restricted', validated_by TEXT,
            validated_at TEXT, history_json TEXT NOT NULL DEFAULT '[]')""")
        db.commit()
        db.close()
        migrated = HeritageStorage(legacy_path)
        result = migrated.get("not-there")
        self.assertIsNone(result)
        with sqlite3.connect(legacy_path) as db:
            self.assertIn("collector_id", {row[1] for row in db.execute("PRAGMA table_info(heritage_records)")})

    def test_sql_injection_id(self):
        self.assertIsNone(self.store.get("' OR 1=1 --"))


if __name__ == "__main__":
    unittest.main()
