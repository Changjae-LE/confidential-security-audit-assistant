from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.analysis_service import get_analysis_snapshot
from app.services.evidence_service import replace_evidence_content


client = TestClient(app)


def _run_cloudtrail_analysis() -> tuple[str, str]:
    sample_path = Path(__file__).parents[2] / "samples" / "cloudtrail_suspicious_iam.json"
    upload_response = client.post(
        "/api/evidence/upload",
        files={
            "file": (
                "cloudtrail_suspicious_iam.json",
                sample_path.read_bytes(),
                "application/json",
            )
        },
    )
    evidence_id = upload_response.json()["evidence_id"]
    analysis_response = client.post(f"/api/analysis/run/{evidence_id}")
    return evidence_id, analysis_response.json()["analysis_id"]


def test_get_verification_record() -> None:
    _, analysis_id = _run_cloudtrail_analysis()

    response = client.get(f"/api/verification/{analysis_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["analysis_id"] == analysis_id
    assert body["verification_status"] == "COMMITTED"
    assert body["committed_at"]
    assert body["mock_tx_id"].startswith("MOCK-MIDNIGHT-")


def test_verification_success() -> None:
    _, analysis_id = _run_cloudtrail_analysis()

    response = client.post(f"/api/verification/{analysis_id}/verify")

    assert response.status_code == 200
    body = response.json()
    assert body["verification_status"] == "VERIFIED"
    assert body["mismatch_reason"] is None
    assert body["input_hash_match"] is True
    assert body["policy_hash_match"] is True
    assert body["result_hash_match"] is True


def test_verification_detects_input_hash_mismatch() -> None:
    evidence_id, analysis_id = _run_cloudtrail_analysis()
    replace_evidence_content(evidence_id, b'{"Records":[]}')

    response = client.post(f"/api/verification/{analysis_id}/verify")

    assert response.status_code == 200
    body = response.json()
    assert body["verification_status"] == "FAILED"
    assert body["mismatch_reason"] == "Input hash mismatch"
    assert body["input_hash_match"] is False


def test_verification_detects_policy_hash_mismatch() -> None:
    _, analysis_id = _run_cloudtrail_analysis()
    snapshot = get_analysis_snapshot(analysis_id)
    assert snapshot is not None
    snapshot["policy_payload"] = {"version": "policy-v2", "rule_ids": []}

    response = client.post(f"/api/verification/{analysis_id}/verify")

    assert response.status_code == 200
    body = response.json()
    assert body["verification_status"] == "FAILED"
    assert body["mismatch_reason"] == "Policy hash mismatch"
    assert body["policy_hash_match"] is False


def test_verification_detects_result_hash_mismatch() -> None:
    _, analysis_id = _run_cloudtrail_analysis()
    snapshot = get_analysis_snapshot(analysis_id)
    assert snapshot is not None
    snapshot["result_payload"] = {"tampered": True}

    response = client.post(f"/api/verification/{analysis_id}/verify")

    assert response.status_code == 200
    body = response.json()
    assert body["verification_status"] == "FAILED"
    assert body["mismatch_reason"] == "Result hash mismatch"
    assert body["result_hash_match"] is False
