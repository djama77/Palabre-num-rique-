"""Local archive creation endpoint for the SQLite-backed heritage application."""
import json
import os
import uuid
from email import policy
from email.parser import BytesParser
from pathlib import Path
from urllib.parse import urlsplit

from workflow import HeritageRecord, Status

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".webm", ".mp4"}


def _multipart_fields(content_type, body):
    message = BytesParser(policy=policy.default).parsebytes(
        ("Content-Type: " + content_type + "\r\nMIME-Version: 1.0\r\n\r\n").encode("ascii") + body
    )
    if not message.is_multipart():
        raise ValueError("Formulaire multipart invalide")
    fields = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        payload = part.get_payload(decode=True) or b""
        filename = part.get_filename()
        fields[name] = {"value": payload, "filename": filename} if filename is not None else {
            "value": payload.decode(part.get_content_charset() or "utf-8", errors="replace"),
            "filename": None,
        }
    return fields


def create_local_archive(store, title, audio_bytes, extension, consent, transcript=""):
    """Persist an original audio file and a draft record in the local SQLite store."""
    title = str(title or "").strip()
    transcript = str(transcript or "").strip()
    extension = str(extension or "").lower()
    if not title or len(title) > 300:
        raise ValueError("Le titre est obligatoire (300 caractères maximum)")
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Format audio non accepté")
    if not consent:
        raise PermissionError("Le consentement est obligatoire")
    if not isinstance(audio_bytes, bytes) or not audio_bytes or len(audio_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Audio vide ou supérieur à 100 Mo")

    db_path = Path(store.db_path).resolve()
    archive_dir = db_path.parent / "audio"
    archive_dir.mkdir(parents=True, exist_ok=True)
    record_id = uuid.uuid4().hex
    relative_path = (Path("audio") / (record_id + extension)).as_posix()
    final_path = db_path.parent / relative_path
    temp_path = final_path.with_suffix(final_path.suffix + ".tmp")
    record = HeritageRecord(
        id=record_id,
        title_so=title,
        original_audio_path=relative_path,
        consent_recorded=True,
        status=Status.DRAFT,
        transcript_so=transcript,
    )
    try:
        temp_path.write_bytes(audio_bytes)
        os.replace(temp_path, final_path)
        store.save(record)
    except Exception:
        temp_path.unlink(missing_ok=True)
        final_path.unlink(missing_ok=True)
        raise
    return {
        "id": record.id,
        "title_so": record.title_so,
        "status": record.status.value,
        "original_audio_path": record.original_audio_path,
        "transcript_saved": bool(record.transcript_so),
    }


def local_archive_post(handler):
    """Handle a same-origin loopback multipart upload and return the saved draft."""
    def reply(status, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.send_header("Content-Length", str(len(payload)))
        handler.end_headers()
        handler.wfile.write(payload)

    if urlsplit(handler.path).path != "/api/local/archives":
        return reply(404, {"error": "Route inconnue"})
    if handler.client_address[0] not in ("127.0.0.1", "::1"):
        return reply(403, {"error": "Accès local uniquement"})
    host = handler.headers.get("Host", "")
    origin = handler.headers.get("Origin", "")
    if host not in ("127.0.0.1:%s" % handler.server.server_port,
                    "localhost:%s" % handler.server.server_port,
                    "[::1]:%s" % handler.server.server_port):
        return reply(403, {"error": "Hôte non autorisé"})
    if origin not in ("http://" + host,):
        return reply(403, {"error": "Origine non autorisée"})
    if handler.headers.get("X-Consentement") != "oui":
        return reply(403, {"error": "Consentement requis"})
    content_type = handler.headers.get("Content-Type", "")
    if not content_type.lower().startswith("multipart/form-data;"):
        return reply(415, {"error": "Formulaire multipart requis"})
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        length = 0
    if length <= 0 or length > MAX_UPLOAD_BYTES + 1024 * 1024:
        return reply(413, {"error": "Audio vide ou supérieur à 100 Mo"})
    try:
        body = handler.rfile.read(length)
        if len(body) != length:
            raise ValueError("Envoi incomplet")
        fields = _multipart_fields(content_type, body)
        audio = fields.get("audio")
        if not audio or not audio["filename"]:
            raise ValueError("Fichier audio requis")
        extension = Path(audio["filename"]).suffix.lower()
        saved = create_local_archive(
            handler.store,
            fields.get("title", {}).get("value", ""),
            audio["value"],
            extension,
            consent=True,
            transcript=fields.get("transcript", {}).get("value", ""),
        )
        return reply(201, {"archive": saved})
    except PermissionError as exc:
        return reply(403, {"error": str(exc)})
    except (ValueError, UnicodeError) as exc:
        return reply(400, {"error": str(exc)})
    except Exception:
        return reply(500, {"error": "Enregistrement local impossible. Vérifiez le stockage SQLite et le dossier audio."})



def local_archive_get(handler):
    """List locally saved drafts or stream an archive's original audio."""
    path = urlsplit(handler.path).path
    if path == "/api/local/archives":
        with handler.store._connect() as db:
            rows = db.execute(
                "SELECT id,title_so,status,transcript_so,original_audio_path,consent_recorded "
                "FROM heritage_records ORDER BY rowid DESC LIMIT 200"
            ).fetchall()
        payload = json.dumps({"archives": [
            {"id": row[0], "title_so": row[1], "status": row[2],
             "transcript_so": row[3], "original_audio_path": row[4],
             "consent_recorded": bool(row[5])}
            for row in rows
        ]}, ensure_ascii=False).encode("utf-8")
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.send_header("Content-Length", str(len(payload)))
        handler.end_headers()
        handler.wfile.write(payload)
        return True

    prefix = "/api/local/archives/audio/"
    if path.startswith(prefix):
        record_id = path[len(prefix):]
        if not record_id or any(ch not in "0123456789abcdef" for ch in record_id) or len(record_id) != 32:
            handler.send_error(404)
            return True
        record = handler.store.get(record_id)
        if record is None:
            handler.send_error(404)
            return True
        root = Path(handler.store.db_path).resolve().parent
        audio_path = (root / record.original_audio_path).resolve()
        if root not in audio_path.parents or not audio_path.is_file():
            handler.send_error(404)
            return True
        import mimetypes
        payload_size = audio_path.stat().st_size
        handler.send_response(200)
        handler.send_header("Content-Type", mimetypes.guess_type(audio_path.name)[0] or "application/octet-stream")
        handler.send_header("Content-Length", str(payload_size))
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.end_headers()
        with audio_path.open("rb") as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                handler.wfile.write(chunk)
        return True
    return False
