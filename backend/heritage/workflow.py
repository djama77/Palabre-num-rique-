"""Core validation workflow for Palabre Numérique (framework independent).

Draft records never become public without human validation.
The calling API must authenticate and authorize each actor.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

class Status(str, Enum):
    DRAFT = "draft"
    TRANSCRIBED = "transcribed"
    REVIEW = "review"
    VALIDATED = "validated"
    REJECTED = "rejected"

@dataclass
class HeritageRecord:
    id: str
    title_so: str
    original_audio_path: str
    consent_recorded: bool
    status: Status = Status.DRAFT
    transcript_so: str = ""
    translation_fr: str = ""
    access_level: str = "restricted"
    validated_by: Optional[str] = None
    validated_at: Optional[str] = None
    history: list = field(default_factory=list)

    def attach_transcription(self, transcript: str, actor: str):
        if self.status != Status.DRAFT or not transcript.strip():
            raise ValueError("Transcription impossible dans cet état")
        self.transcript_so = transcript.strip()
        self.status = Status.TRANSCRIBED
        self.history.append(("transcribed", actor))

    def submit_for_review(self, actor: str):
        if self.status != Status.TRANSCRIBED:
            raise ValueError("Transcription requise avant validation")
        self.status = Status.REVIEW
        self.history.append(("review", actor))

    def validate(self, sage_id: str, *, is_authorized_sage: bool):
        if not is_authorized_sage or not sage_id:
            raise PermissionError("Validation réservée aux Sages autorisés")
        if self.status != Status.REVIEW or not self.consent_recorded:
            raise ValueError("Consentement et examen requis")
        self.status = Status.VALIDATED
        self.validated_by = sage_id
        self.validated_at = datetime.now(timezone.utc).isoformat()
        self.history.append(("validated", sage_id))

    def publish(self, actor: str, *, publication_authorized: bool):
        if self.status != Status.VALIDATED or not publication_authorized:
            raise PermissionError("Publication interdite")
        self.access_level = "public"
        self.history.append(("published", actor))

    def public_payload(self):
        if self.status != Status.VALIDATED or self.access_level != "public":
            raise PermissionError("Récit non publiable")
        return {
            "id": self.id,
            "title_so": self.title_so,
            "translation_fr": self.translation_fr,
            "validation_status": "validated",
            "access_level": "public",
        }
