import unittest
from workflow import HeritageRecord, Status

class HeritageWorkflowTests(unittest.TestCase):
    def make_record(self, consent=True):
        return HeritageRecord("r1", "Sheeko", "secure://original", consent)

    def test_not_public_by_default(self):
        with self.assertRaises(PermissionError):
            self.make_record().public_payload()

    def test_full_validated_workflow(self):
        r = self.make_record()
        r.attach_transcription("Qoraal", "collector")
        r.submit_for_review("editor")
        r.validate("sage-1", is_authorized_sage=True)
        with self.assertRaises(PermissionError):
            r.public_payload()
        r.publish("admin", publication_authorized=True)
        self.assertEqual(r.public_payload()["validation_status"], "validated")
        self.assertEqual(r.status, Status.VALIDATED)

    def test_cannot_validate_without_consent(self):
        r = self.make_record(consent=False)
        r.attach_transcription("Qoraal", "collector")
        r.submit_for_review("editor")
        with self.assertRaises(ValueError):
            r.validate("sage-1", is_authorized_sage=True)

    def test_unauthorized_sage(self):
        r = self.make_record()
        r.attach_transcription("Qoraal", "collector")
        r.submit_for_review("editor")
        with self.assertRaises(PermissionError):
            r.validate("sage-1", is_authorized_sage=False)

    def test_no_publication_before_validation(self):
        with self.assertRaises(PermissionError):
            self.make_record().publish("admin", publication_authorized=True)

if __name__ == "__main__":
    unittest.main()
