from app.schemas.finding import Finding


class ComplianceAgent:
    def assess(self, events: list[dict], findings: list[Finding]) -> str:
        if not events:
            return "NEEDS_REVIEW"
        if findings:
            return "FAILED"
        return "PASS"

    def risk_level(self, findings: list[Finding]) -> str:
        severity_rank = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1,
        }
        if not findings:
            return "LOW"
        return max(findings, key=lambda finding: severity_rank.get(finding.severity, 0)).severity.upper()
