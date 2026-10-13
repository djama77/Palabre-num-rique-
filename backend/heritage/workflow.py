"""Heritage workflow without a Sages validation step.

Consent and explicit publication authorization remain mandatory.
Authentication and operator permissions must be enforced by the calling server.
"""
from dataclasses import dataclass, field
from enum import Enum

class Status(str, Enum):
    DRAFT = "draft"
    TRANSCRIBED = "transcribed"
    PUBLISHED = "published"

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
    validated_by: str | None = None  # legacy SQLite compatibility only
    validated_at: str | None = None  # legacy SQLite compatibility only
    history: list = field(default_factory=list)

    def attach_transcription(self, transcript: str, actor: str):
        if self.status != Status.DRAFT or not transcript.strip():
            raise ValueError("Transcription impossible dans cet état")
        self.transcript_so = transcript.strip()
        self.status = Status.TRANSCRIBED
        self.history.append(("transcribed", actor))

    def publish(self, actor: str, *, publication_authorized: bool):
        if not publication_authorized or not actor:
            raise PermissionError("Autorisation de publication requise")
        if not self.consent_recorded or self.status != Status.TRANSCRIBED:
            raise PermissionError("Consentement et transcription requis")
        self.status = Status.PUBLISHED
        self.access_level = "public"
        self.history.append(("published", actor))

    def public_payload(self):
        if not self.consent_recorded or self.status != Status.PUBLISHED or self.access_level != "public":
            raise PermissionError("Récit non publiable")
        return {
            "id": self.id,
            "title_so": self.title_so,
            "translation_fr": self.translation_fr,
            "publication_status": "published",
            "access_level": "public",
        }
