import os

import httpx

from app.schemas.finding import Finding


class LLMReportEnhancer:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def enhance(
        self,
        deterministic_report: str,
        findings: list[Finding],
        risk_level: str,
        compliance_status: str,
    ) -> str:
        if not self.api_key:
            return deterministic_report

        payload = self._safe_payload(findings, risk_level, compliance_status)
        try:
            enhanced_text = self._call_openai(payload)
        except httpx.HTTPError:
            return deterministic_report

        if not enhanced_text:
            return deterministic_report

        return "\n".join(
            [
                deterministic_report,
                "",
                "## LLM-Enhanced Executive Summary",
                enhanced_text.strip(),
            ]
        )

    def _safe_payload(
        self,
        findings: list[Finding],
        risk_level: str,
        compliance_status: str,
    ) -> dict:
        return {
            "risk_level": risk_level,
            "compliance_status": compliance_status,
            "findings": [
                {
                    "rule_id": finding.rule_id,
                    "title": finding.title,
                    "severity": finding.severity,
                    "evidence_summary": finding.evidence_summary,
                    "recommended_action": finding.recommended_action,
                    "confidence_score": finding.confidence_score,
                }
                for finding in findings
            ],
        }

    def _call_openai(self, payload: dict) -> str:
        instructions = (
            "You improve security audit report wording. Use only the provided finding summaries. "
            "Do not change severity, risk_level, compliance_status, rule IDs, or hash-related claims. "
            "Do not infer facts beyond the provided summaries. Return concise markdown with an "
            "executive summary and improved recommended actions."
        )
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "instructions": instructions,
                "input": [{"role": "user", "content": [{"type": "input_text", "text": str(payload)}]}],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        body = response.json()
        output_text = body.get("output_text")
        if isinstance(output_text, str):
            return output_text

        # Minimal fallback parser for Responses API content blocks.
        output = body.get("output", [])
        if isinstance(output, list):
            parts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if isinstance(content, dict) and isinstance(content.get("text"), str):
                        parts.append(content["text"])
            return "\n".join(parts)

        return ""
