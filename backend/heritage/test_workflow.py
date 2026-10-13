import unittest
from workflow import HeritageRecord, Status

class HeritageWorkflowTests(unittest.TestCase):
    def make_record(self, consent=True):
        return HeritageRecord("r1", "Sheeko", "secure://original", consent)

    def test_private_by_default(self):
        with self.assertRaises(PermissionError):
            self.make_record().public_payload()

    def test_publish_without_sage_validation(self):
        r = self.make_record()
        r.attach_transcription("Qoraal", "collector")
        r.publish("publisher", publication_authorized=True)
        self.assertEqual(r.status, Status.PUBLISHED)
        self.assertEqual(r.public_payload()["publication_status"], "published")

    def test_no_publication_without_consent(self):
        r = self.make_record(False)
        r.attach_transcription("Qoraal", "collector")
        with self.assertRaises(PermissionError):
            r.publish("publisher", publication_authorized=True)

    def test_no_publication_without_authorization(self):
        r = self.make_record()
        r.attach_transcription("Qoraal", "collector")
        with self.assertRaises(PermissionError):
            r.publish("publisher", publication_authorized=False)

    def test_no_publication_before_transcription(self):
        with self.assertRaises(PermissionError):
            self.make_record().publish("publisher", publication_authorized=True)

if __name__ == "__main__":
    unittest.main()
