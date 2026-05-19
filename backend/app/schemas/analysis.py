from pydantic import BaseModel

from app.schemas.finding import Finding
from app.schemas.verification_record import VerificationRecord


class AnalysisPlaceholderResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


class AnalysisRunResponse(BaseModel):
    analysis_id: str
    findings: list[Finding]
    risk_level: str
    compliance_status: str
    report: str
    verification_record: VerificationRecord
