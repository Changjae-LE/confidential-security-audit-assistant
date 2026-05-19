from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.evidence import EvidenceUploadResponse
from app.services.evidence_service import is_allowed_upload, store_evidence_metadata

router = APIRouter()

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=EvidenceUploadResponse)
async def upload_evidence(file: UploadFile = File(...)) -> EvidenceUploadResponse:
    if not is_allowed_upload(file.filename or "", file.content_type):
        raise HTTPException(status_code=400, detail="Only CSV or JSON uploads are supported.")

    content = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB upload limit.")

    return store_evidence_metadata(
        filename=file.filename or "uploaded-evidence",
        content_type=file.content_type,
        content=content,
    )
