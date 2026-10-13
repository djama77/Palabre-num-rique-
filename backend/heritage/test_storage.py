import os
import tempfile
import unittest
from storage import HeritageStorage
from workflow import HeritageRecord

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=HeritageStorage(os.path.join(self.temp.name,"heritage.sqlite3"))

    def tearDown(self):
        self.temp.cleanup()

    def test_roundtrip_private(self):
        record=HeritageRecord("r1","Sheeko","private/audio.wav",True)
        self.store.save(record)
        result=self.store.get("r1")
        self.assertEqual(result.title_so,"Sheeko")
        with self.assertRaises(PermissionError):
            self.store.get_public("r1")
        self.assertEqual(self.store.list_public(),[])

    def test_published_public(self):
        record=HeritageRecord("r2","Sheeko","private/audio.wav",True)
        record.attach_transcription("Qoraal","collector")
        record.translation_fr="Récit traduit"
        record.publish("admin",publication_authorized=True)
        self.store.save(record)
        public=self.store.get_public("r2")
        self.assertEqual(public["translation_fr"],"Récit traduit")
        self.assertNotIn("original_audio_path",public)
        self.assertEqual(len(self.store.list_public()),1)

    def test_sql_injection_id(self):
        self.assertIsNone(self.store.get("' OR 1=1 --"))

if __name__=="__main__":
    unittest.main()
