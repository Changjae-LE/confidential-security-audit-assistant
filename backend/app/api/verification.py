from fastapi import APIRouter, HTTPException

from app.schemas.verification import VerificationResult
from app.schemas.verification_record import VerificationRecord
from app.services.verification_service import (
    VerificationNotFoundError,
    get_verification_record,
    verify_analysis,
)

router = APIRouter()


@router.get("/{analysis_id}", response_model=VerificationRecord)
def get_verification(analysis_id: str) -> VerificationRecord:
    try:
        return get_verification_record(analysis_id)
    except VerificationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Verification record not found.") from exc


@router.post("/{analysis_id}/verify", response_model=VerificationResult)
def verify_verification_record(analysis_id: str) -> VerificationResult:
    try:
        return verify_analysis(analysis_id)
    except VerificationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Verification record not found.") from exc
