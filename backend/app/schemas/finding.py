from pydantic import BaseModel, Field


class Finding(BaseModel):
    title: str
    severity: str
    evidence_summary: str
    affected_asset: str
    rule_id: str
    recommended_action: str
    confidence_score: float = Field(ge=0.0, le=1.0)
