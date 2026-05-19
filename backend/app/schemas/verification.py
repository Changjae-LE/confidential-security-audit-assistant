from pydantic import BaseModel

from app.schemas.verification_record import VerificationRecord


class VerificationPlaceholderResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


class VerificationResult(BaseModel):
    analysis_id: str
    verification_status: str
    mismatch_reason: str | None = None
    input_hash_match: bool
    policy_hash_match: bool
    result_hash_match: bool
    record: VerificationRecord
