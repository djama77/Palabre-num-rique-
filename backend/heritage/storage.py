"""SQLite persistence for Palabre Numérique heritage records.

Prototype repository: use a protected database file on the server, never in a
public/static directory. No original audio bytes are stored in this database.
"""
import json
import sqlite3
from pathlib import Path
from workflow import HeritageRecord, Status

SCHEMA = """
CREATE TABLE IF NOT EXISTS heritage_records (
 id TEXT PRIMARY KEY,
 title_so TEXT NOT NULL,
 original_audio_path TEXT NOT NULL,
 consent_recorded INTEGER NOT NULL CHECK(consent_recorded IN (0,1)),
 status TEXT NOT NULL,
 transcript_so TEXT NOT NULL DEFAULT '',
 translation_fr TEXT NOT NULL DEFAULT '',
 access_level TEXT NOT NULL DEFAULT 'restricted',
 validated_by TEXT,
 validated_at TEXT,
 history_json TEXT NOT NULL DEFAULT '[]'
);
"""

class HeritageStorage:
    def __init__(self, db_path):
        self.db_path = str(Path(db_path))
        with self._connect() as db:
            db.executescript(SCHEMA)

    def _connect(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def save(self, record):
        if not isinstance(record, HeritageRecord):
            raise TypeError("HeritageRecord requis")
        with self._connect() as db:
            db.execute("""
                INSERT INTO heritage_records
                (id,title_so,original_audio_path,consent_recorded,status,
                 transcript_so,translation_fr,access_level,validated_by,
                 validated_at,history_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                 title_so=excluded.title_so,
                 original_audio_path=excluded.original_audio_path,
                 consent_recorded=excluded.consent_recorded,
                 status=excluded.status,
                 transcript_so=excluded.transcript_so,
                 translation_fr=excluded.translation_fr,
                 access_level=excluded.access_level,
                 validated_by=excluded.validated_by,
                 validated_at=excluded.validated_at,
                 history_json=excluded.history_json
            """, (
                record.id,record.title_so,record.original_audio_path,
                int(record.consent_recorded),record.status.value,
                record.transcript_so,record.translation_fr,record.access_level,
                record.validated_by,record.validated_at,
                json.dumps(record.history,ensure_ascii=False)
            ))

    def get(self, record_id):
        with self._connect() as db:
            row = db.execute("SELECT * FROM heritage_records WHERE id=?",(record_id,)).fetchone()
        if row is None:
            return None
        return HeritageRecord(
            id=row[0],title_so=row[1],original_audio_path=row[2],
            consent_recorded=bool(row[3]),status=Status(row[4]),
            transcript_so=row[5],translation_fr=row[6],
            access_level=row[7],validated_by=row[8],validated_at=row[9],
            history=json.loads(row[10])
        )

    def get_public(self, record_id):
        record = self.get(record_id)
        if record is None:
            return None
        return record.public_payload()

    def list_public(self, limit=30):
        limit=max(1,min(int(limit),100))
        with self._connect() as db:
            ids=db.execute(
                "SELECT id FROM heritage_records WHERE status=? AND access_level=? ORDER BY id LIMIT ?",
                (Status.PUBLISHED.value,"public",limit)
            ).fetchall()
        return [self.get_public(row[0]) for row in ids]
