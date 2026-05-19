from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas.evidence import EvidenceUploadResponse
from app.services.hash_service import sha256_hex

ALLOWED_CONTENT_TYPES = {
    "application/json",
    "text/csv",
}
ALLOWED_EXTENSIONS = {
    ".csv",
    ".json",
}

_evidence_metadata: dict[str, EvidenceUploadResponse] = {}
_evidence_content: dict[str, bytes] = {}


def is_allowed_upload(filename: str, content_type: str | None) -> bool:
    extension = Path(filename).suffix.lower()
    return content_type in ALLOWED_CONTENT_TYPES and extension in ALLOWED_EXTENSIONS


def store_evidence_metadata(
    filename: str,
    content_type: str | None,
    content: bytes,
) -> EvidenceUploadResponse:
    evidence_id = f"EVD-{uuid4().hex}"
    safe_filename = Path(filename).name
    metadata = EvidenceUploadResponse(
        evidence_id=evidence_id,
        filename=safe_filename,
        content_type=content_type or "application/octet-stream",
        input_hash=sha256_hex(content),
        uploaded_at=datetime.now(timezone.utc),
    )
    _evidence_metadata[evidence_id] = metadata
    _evidence_content[evidence_id] = content
    return metadata


def get_evidence_metadata(evidence_id: str) -> EvidenceUploadResponse | None:
    return _evidence_metadata.get(evidence_id)


def get_evidence_content(evidence_id: str) -> bytes | None:
    return _evidence_content.get(evidence_id)


def replace_evidence_content(evidence_id: str, content: bytes) -> None:
    if evidence_id in _evidence_content:
        _evidence_content[evidence_id] = content
