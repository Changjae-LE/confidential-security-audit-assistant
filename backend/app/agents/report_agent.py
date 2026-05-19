from app.schemas.finding import Finding
from app.services.llm_report_enhancer import LLMReportEnhancer


class ReportAgent:
    def __init__(self, enhancer: LLMReportEnhancer | None = None) -> None:
        self.enhancer = enhancer or LLMReportEnhancer()

    def generate(self, analysis_id: str, findings: list[Finding], risk_level: str, compliance_status: str) -> str:
        lines = [
            f"# Security Audit Report: {analysis_id}",
            "",
            f"- Risk Level: {risk_level}",
            f"- Compliance Status: {compliance_status}",
            f"- Finding Count: {len(findings)}",
            "",
            "## Findings",
        ]

        if not findings:
            lines.append("No deterministic policy findings were detected.")
        else:
            for finding in findings:
                lines.extend(
                    [
                        f"### {finding.title}",
                        f"- Rule: {finding.rule_id}",
                        f"- Severity: {finding.severity}",
                        f"- Affected Asset: {finding.affected_asset}",
                        f"- Evidence Summary: {finding.evidence_summary}",
                        f"- Recommended Action: {finding.recommended_action}",
                        f"- Confidence Score: {finding.confidence_score:.2f}",
                    ]
                )

        deterministic_report = "\n".join(lines)
        return self.enhancer.enhance(
            deterministic_report=deterministic_report,
            findings=findings,
            risk_level=risk_level,
            compliance_status=compliance_status,
        )
