from datetime import datetime

from pydantic import BaseModel


class VerificationRecord(BaseModel):
    analysis_id: str
    input_hash: str
    policy_hash: str
    result_hash: str
    risk_level: str
    compliance_status: str
    verification_status: str
    committed_at: datetime | None = None
    mock_tx_id: str
