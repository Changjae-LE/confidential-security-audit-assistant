from datetime import datetime

from pydantic import BaseModel


class EvidenceUploadResponse(BaseModel):
    evidence_id: str
    filename: str
    content_type: str
    input_hash: str
    uploaded_at: datetime
