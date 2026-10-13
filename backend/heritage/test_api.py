import os
import tempfile
import unittest
from api import public_response
from storage import HeritageStorage
from workflow import HeritageRecord

class APITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = HeritageStorage(os.path.join(self.temp.name, "db.sqlite3"))

    def tearDown(self):
        self.temp.cleanup()

    def test_health(self):
        status, result = public_response(self.store, "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "ok")

    def test_private_record_not_exposed(self):
        self.store.save(HeritageRecord("secret", "Private", "secret.wav", True))
        status, _ = public_response(self.store, "/api/heritage/public/secret")
        self.assertEqual(status, 404)
        status, result = public_response(self.store, "/api/heritage/public")
        self.assertEqual(status, 200)
        self.assertEqual(result["records"], [])

    def test_published_record(self):
        r = HeritageRecord("public1", "Sheeko", "private.wav", True)
        r.attach_transcription("Qoraal", "collector")
        r.submit_for_review("editor")
        r.validate("sage", is_authorized_sage=True)
        r.translation_fr = "Traduction relue"
        r.publish("admin", publication_authorized=True)
        self.store.save(r)
        status, result = public_response(self.store, "/api/heritage/public/public1")
        self.assertEqual(status, 200)
        self.assertEqual(result["translation_fr"], "Traduction relue")
        self.assertNotIn("original_audio_path", result)

    def test_invalid_id(self):
        status, _ = public_response(self.store, "/api/heritage/public/a%2Fb")
        self.assertEqual(status, 400)

if __name__ == "__main__":
    unittest.main()
