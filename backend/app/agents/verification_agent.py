from app.schemas.finding import Finding
from app.schemas.verification_record import VerificationRecord
from app.services.hash_service import sha256_json
from app.services.midnight_adapter import MockMidnightAdapter

POLICY_PAYLOAD = {
    "version": "policy-v1",
    "rule_ids": [
        "POL-ROOT-MFA-001",
        "POL-IAM-PRIV-001",
        "POL-S3-PUBLIC-001",
        "POL-SG-OPEN-001",
        "POL-CVE-CRITICAL-001",
        "POL-WEB-500-001",
    ],
}


def build_result_payload(
    findings: list[Finding],
    risk_level: str,
    compliance_status: str,
    report: str,
) -> dict:
    return {
        "findings": [finding.model_dump() for finding in findings],
        "risk_level": risk_level,
        "compliance_status": compliance_status,
        "report": report,
    }


class VerificationAgent:
    def __init__(self, midnight_adapter: MockMidnightAdapter | None = None) -> None:
        self.midnight_adapter = midnight_adapter or MockMidnightAdapter()

    def verify(
        self,
        analysis_id: str,
        input_hash: str,
        findings: list[Finding],
        risk_level: str,
        compliance_status: str,
        report: str,
    ) -> VerificationRecord:
        result_payload = build_result_payload(findings, risk_level, compliance_status, report)
        pending_record = VerificationRecord(
            analysis_id=analysis_id,
            input_hash=input_hash,
            policy_hash=sha256_json(POLICY_PAYLOAD),
            result_hash=sha256_json(result_payload),
            risk_level=risk_level,
            compliance_status=compliance_status,
            verification_status="PENDING",
            mock_tx_id="",
        )
        return self.midnight_adapter.commit(pending_record)
