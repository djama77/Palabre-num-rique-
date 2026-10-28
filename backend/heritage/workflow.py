"""Lifecycle rules for private heritage records and Sage-approved publication."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    validated_by: str | None = None
    validated_at: str | None = None
    history: list = field(default_factory=list)
    collector_id: str | None = None

    def attach_transcription(self, transcript: str, actor: str):
        if self.status != Status.DRAFT or not transcript.strip() or not actor:
            raise ValueError("Transcription impossible dans cet état")
        self.transcript_so = transcript.strip()
        self.status = Status.TRANSCRIBED
        self.history.append(("transcribed", actor))

    def validate_by_sage(self, actor: str, *, role: str):
        if role.strip().lower() != "sage" or not actor:
            raise PermissionError("Validation réservée à un Sage authentifié")
        if self.status != Status.TRANSCRIBED or not self.transcript_so.strip():
            raise PermissionError("Le récit doit être transcrit avant validation")
        if not self.consent_recorded:
            raise PermissionError("Consentement requis avant validation")
        if not self.collector_id:
            raise PermissionError("Identité du collecteur manquante : validation bloquée")
        if actor == self.collector_id:
            raise PermissionError("Auto-validation interdite")
        self.validated_by = actor
        self.validated_at = datetime.now(timezone.utc).isoformat()
        self.history.append(("sage_approved", actor))

    def publish(self, actor: str, *, publication_authorized: bool):
        if not actor or not publication_authorized:
            raise PermissionError("Autorisation explicite de publication requise")
        if not self.consent_recorded or self.status != Status.TRANSCRIBED:
            raise PermissionError("Consentement et transcription requis")
        if not self.validated_by or not self.validated_at:
            raise PermissionError("Validation préalable du Collège des Sages requise")
        self.status = Status.PUBLISHED
        self.access_level = "public"
        self.history.append(("published", actor))

    def revoke_consent(self, actor: str):
        if not actor:
            raise PermissionError("Acteur requis pour tracer la révocation")
        self.consent_recorded = False
        self.access_level = "restricted"
        if self.status == Status.PUBLISHED:
            self.status = Status.DRAFT
        # A revoked consent invalidates the previous approval as well.
        self.validated_by = None
        self.validated_at = None
        self.history.append(("consent_revoked", actor))

    def public_payload(self):
        if (
            not self.consent_recorded
            or self.status != Status.PUBLISHED
            or self.access_level != "public"
            or not self.validated_by
            or not self.validated_at
        ):
            raise PermissionError("Récit non publiable")
        return {
            "id": self.id,
            "title_so": self.title_so,
            "translation_fr": self.translation_fr,
            "publication_status": "published",
            "access_level": "public",
        }
