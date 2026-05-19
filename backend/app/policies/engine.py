from collections.abc import Iterable

from app.policies.rules import POLICY_RULES
from app.schemas.finding import Finding


def evaluate_policies(events: Iterable[dict]) -> list[Finding]:
    normalized_events = list(events)
    findings: list[Finding] = []

    for rule in POLICY_RULES:
        finding = rule(normalized_events)
        if finding is not None:
            findings.append(finding)

    return findings
