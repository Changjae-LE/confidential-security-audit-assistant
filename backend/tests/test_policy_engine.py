from pathlib import Path

from app.agents.ingestion_agent import IngestionAgent
from app.policies.engine import evaluate_policies


def test_root_account_login_without_mfa_is_critical() -> None:
    findings = evaluate_policies(
        [
            {
                "eventName": "ConsoleLogin",
                "userIdentity": {"type": "Root"},
                "additionalEventData": {"MFAUsed": "No"},
            }
        ]
    )

    assert findings[0].rule_id == "POL-ROOT-MFA-001"
    assert findings[0].severity == "Critical"


def test_iam_privilege_escalation_is_high() -> None:
    findings = evaluate_policies(
        [
            {
                "eventName": "AttachUserPolicy",
                "requestParameters": {
                    "userName": "alice",
                    "policyArn": "arn:aws:iam::aws:policy/AdministratorAccess",
                },
            }
        ]
    )

    assert findings[0].rule_id == "POL-IAM-PRIV-001"
    assert findings[0].severity == "High"
    assert findings[0].affected_asset == "alice"


def test_public_s3_bucket_is_high() -> None:
    findings = evaluate_policies(
        [
            {
                "resource_type": "s3_bucket",
                "bucket": "audit-demo-bucket",
                "acl": {"grants": [{"grantee": "AllUsers", "permission": "READ"}]},
            }
        ]
    )

    assert findings[0].rule_id == "POL-S3-PUBLIC-001"
    assert findings[0].severity == "High"


def test_security_group_open_to_world_is_high() -> None:
    findings = evaluate_policies(
        [
            {
                "resource_type": "security_group",
                "group_id": "sg-123",
                "ingress": [{"from_port": 22, "cidr": "0.0.0.0/0"}],
            }
        ]
    )

    assert findings[0].rule_id == "POL-SG-OPEN-001"
    assert findings[0].severity == "High"


def test_critical_cve_with_cvss_at_least_nine_is_critical() -> None:
    findings = evaluate_policies(
        [
            {
                "cve": "CVE-2026-0001",
                "cvss": 9.8,
                "asset": "api-server-1",
            }
        ]
    )

    assert findings[0].rule_id == "POL-CVE-CRITICAL-001"
    assert findings[0].severity == "Critical"


def test_web_attack_followed_by_500_is_high() -> None:
    findings = evaluate_policies(
        [
            {
                "source_ip": "203.0.113.10",
                "path": "/login?next=../etc/passwd",
                "status": 403,
            },
            {
                "source_ip": "203.0.113.10",
                "url": "https://app.example.test/login",
                "status": 500,
            },
        ]
    )

    assert findings[0].rule_id == "POL-WEB-500-001"
    assert findings[0].severity == "High"


def test_non_matching_events_return_no_findings() -> None:
    findings = evaluate_policies(
        [
            {
                "eventName": "ConsoleLogin",
                "userIdentity": {"type": "IAMUser"},
                "additionalEventData": {"MFAUsed": "Yes"},
            }
        ]
    )

    assert findings == []


def test_root_login_without_mfa_sample_generates_critical_finding() -> None:
    events = _load_sample("root_login_without_mfa.json")

    findings = evaluate_policies(events)

    assert any(
        finding.rule_id == "POL-ROOT-MFA-001" and finding.severity == "Critical"
        for finding in findings
    )


def test_critical_cve_scan_sample_generates_critical_finding() -> None:
    events = _load_sample("critical_cve_scan_result.json")

    findings = evaluate_policies(events)

    assert any(
        finding.rule_id == "POL-CVE-CRITICAL-001" and finding.severity == "Critical"
        for finding in findings
    )


def _load_sample(filename: str) -> list[dict]:
    sample_path = Path(__file__).parents[2] / "samples" / filename
    return IngestionAgent().normalize(
        sample_path.read_bytes(),
        content_type="application/json",
        filename=filename,
    )
