from uuid import uuid4

from app.agents.verification_agent import POLICY_PAYLOAD, build_result_payload
from app.agents.compliance_agent import ComplianceAgent
from app.agents.ingestion_agent import IngestionAgent
from app.agents.report_agent import ReportAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.verification_agent import VerificationAgent
from app.schemas.analysis import AnalysisRunResponse
from app.services.evidence_service import get_evidence_content, get_evidence_metadata

_analysis_snapshots: dict[str, dict] = {}


class EvidenceNotFoundError(Exception):
    pass


class AnalysisService:
    def __init__(self) -> None:
        self.ingestion_agent = IngestionAgent()
        self.risk_analysis_agent = RiskAnalysisAgent()
        self.compliance_agent = ComplianceAgent()
        self.report_agent = ReportAgent()
        self.verification_agent = VerificationAgent()

    def run(self, evidence_id: str) -> AnalysisRunResponse:
        metadata = get_evidence_metadata(evidence_id)
        content = get_evidence_content(evidence_id)
        if metadata is None or content is None:
            raise EvidenceNotFoundError(evidence_id)

        analysis_id = f"ANL-{uuid4().hex}"
        events = self.ingestion_agent.normalize(content, metadata.content_type, metadata.filename)
        findings = self.risk_analysis_agent.analyze(events)
        compliance_status = self.compliance_agent.assess(events, findings)
        risk_level = self.compliance_agent.risk_level(findings)
        report = self.report_agent.generate(analysis_id, findings, risk_level, compliance_status)
        verification_record = self.verification_agent.verify(
            analysis_id=analysis_id,
            input_hash=metadata.input_hash,
            findings=findings,
            risk_level=risk_level,
            compliance_status=compliance_status,
            report=report,
        )
        _analysis_snapshots[analysis_id] = {
            "evidence_id": evidence_id,
            "policy_payload": POLICY_PAYLOAD,
            "result_payload": build_result_payload(findings, risk_level, compliance_status, report),
        }

        return AnalysisRunResponse(
            analysis_id=analysis_id,
            findings=findings,
            risk_level=risk_level,
            compliance_status=compliance_status,
            report=report,
            verification_record=verification_record,
        )


def get_analysis_snapshot(analysis_id: str) -> dict | None:
    return _analysis_snapshots.get(analysis_id)
