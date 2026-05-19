from app.policies.engine import evaluate_policies
from app.schemas.finding import Finding


class RiskAnalysisAgent:
    def analyze(self, events: list[dict]) -> list[Finding]:
        return evaluate_policies(events)
