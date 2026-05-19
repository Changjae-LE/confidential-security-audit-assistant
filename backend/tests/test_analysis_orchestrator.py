from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_run_analysis_for_cloudtrail_sample() -> None:
    sample_path = Path(__file__).parents[2] / "samples" / "cloudtrail_suspicious_iam.json"
    content = sample_path.read_bytes()

    upload_response = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", content, "application/json")},
    )
    evidence_id = upload_response.json()["evidence_id"]

    analysis_response = client.post(f"/api/analysis/run/{evidence_id}")

    assert analysis_response.status_code == 200
    body = analysis_response.json()
    rule_ids = {finding["rule_id"] for finding in body["findings"]}
    assert body["analysis_id"].startswith("ANL-")
    assert "POL-IAM-PRIV-001" in rule_ids
    assert "POL-ROOT-MFA-001" in rule_ids
    assert body["risk_level"] == "CRITICAL"
    assert body["compliance_status"] == "FAILED"
    assert "# Security Audit Report" in body["report"]

    verification_record = body["verification_record"]
    assert verification_record["analysis_id"] == body["analysis_id"]
    assert verification_record["input_hash"] == upload_response.json()["input_hash"]
    assert verification_record["policy_hash"]
    assert verification_record["result_hash"]
    assert verification_record["verification_status"] == "COMMITTED"
    assert verification_record["committed_at"]
    assert verification_record["mock_tx_id"].startswith("MOCK-MIDNIGHT-")


def test_run_analysis_returns_404_for_missing_evidence() -> None:
    response = client.post("/api/analysis/run/EVD-2026-9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Evidence not found."
