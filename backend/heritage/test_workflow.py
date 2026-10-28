import unittest
from workflow import HeritageRecord, Status


class HeritageWorkflowTests(unittest.TestCase):
    def make_record(self, consent=True, collector_id="collector"):
        return HeritageRecord(
            "r1", "Sheeko", "secure://original", consent,
            collector_id=collector_id
        )

    def transcribed(self, consent=True, collector_id="collector"):
        record = self.make_record(consent, collector_id)
        record.attach_transcription("Qoraal", "transcriber")
        return record

    def test_private_by_default(self):
        with self.assertRaises(PermissionError):
            self.make_record().public_payload()

    def test_publication_requires_sage_validation_and_authorization(self):
        record = self.transcribed()
        with self.assertRaises(PermissionError):
            record.publish("publisher", publication_authorized=True)
        record.validate_by_sage("sage-1", role="sage")
        record.publish("publisher", publication_authorized=True)
        self.assertEqual(record.status, Status.PUBLISHED)
        self.assertEqual(record.public_payload()["publication_status"], "published")

    def test_non_sage_cannot_validate(self):
        record = self.transcribed()
        with self.assertRaises(PermissionError):
            record.validate_by_sage("reviewer", role="transcripteur")

    def test_collector_cannot_validate_own_record(self):
        record = self.transcribed(collector_id="sage-1")
        with self.assertRaises(PermissionError):
            record.validate_by_sage("sage-1", role="sage")

    def test_missing_collector_identity_blocks_validation(self):
        record = self.transcribed(collector_id=None)
        with self.assertRaises(PermissionError):
            record.validate_by_sage("sage-1", role="sage")

    def test_no_publication_without_consent(self):
        record = self.transcribed(consent=False)
        with self.assertRaises(PermissionError):
            record.validate_by_sage("sage-1", role="sage")

    def test_no_publication_without_explicit_authorization(self):
        record = self.transcribed()
        record.validate_by_sage("sage-1", role="sage")
        with self.assertRaises(PermissionError):
            record.publish("publisher", publication_authorized=False)

    def test_no_publication_before_transcription(self):
        with self.assertRaises(PermissionError):
            self.make_record().publish("publisher", publication_authorized=True)

    def test_revocation_removes_public_access(self):
        record = self.transcribed()
        record.validate_by_sage("sage-1", role="sage")
        record.publish("publisher", publication_authorized=True)
        record.revoke_consent("holder")
        with self.assertRaises(PermissionError):
            record.public_payload()
        self.assertEqual(record.access_level, "restricted")


if __name__ == "__main__":
    unittest.main()
