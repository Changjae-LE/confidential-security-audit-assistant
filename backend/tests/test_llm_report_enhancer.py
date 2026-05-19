from app.agents.report_agent import ReportAgent
from app.schemas.finding import Finding
from app.services.llm_report_enhancer import LLMReportEnhancer


def test_report_agent_falls_back_when_openai_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = ReportAgent()
    findings = [
        Finding(
            title="Root account login without MFA",
            severity="Critical",
            evidence_summary="A root console login succeeded without MFA.",
            affected_asset="AWS root account",
            rule_id="POL-ROOT-MFA-001",
            recommended_action="Investigate the root login and require MFA for root account access.",
            confidence_score=0.98,
        )
    ]

    report = agent.generate(
        analysis_id="ANL-2026-0001",
        findings=findings,
        risk_level="CRITICAL",
        compliance_status="FAILED",
    )

    assert "## LLM-Enhanced Executive Summary" not in report
    assert "- Risk Level: CRITICAL" in report
    assert "- Compliance Status: FAILED" in report
    assert "- Severity: Critical" in report
    assert "Investigate the root login" in report


def test_llm_payload_contains_only_finding_summaries() -> None:
    enhancer = LLMReportEnhancer(api_key=None)
    finding = Finding(
        title="Suspicious IAM privilege escalation",
        severity="High",
        evidence_summary="An IAM change granted broad administrative privileges.",
        affected_asset="alice",
        rule_id="POL-IAM-PRIV-001",
        recommended_action="Review the IAM change and revoke excessive permissions.",
        confidence_score=0.92,
    )

    payload = enhancer._safe_payload([finding], "HIGH", "FAILED")

    assert payload == {
        "risk_level": "HIGH",
        "compliance_status": "FAILED",
        "findings": [
            {
                "rule_id": "POL-IAM-PRIV-001",
                "title": "Suspicious IAM privilege escalation",
                "severity": "High",
                "evidence_summary": "An IAM change granted broad administrative privileges.",
                "recommended_action": "Review the IAM change and revoke excessive permissions.",
                "confidence_score": 0.92,
            }
        ],
    }
    assert "affected_asset" not in payload["findings"][0]
