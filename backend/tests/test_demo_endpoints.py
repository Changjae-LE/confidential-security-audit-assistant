import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _upload_and_analyze() -> str:
    sample = Path(__file__).parents[2] / "samples" / "cloudtrail_suspicious_iam.json"
    up = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", sample.read_bytes(), "application/json")},
    )
    an = client.post(f"/api/analysis/run/{up.json()['evidence_id']}")
    return an.json()["analysis_id"]


def test_demo_tamper_endpoints_return_404_without_demo_mode(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_MODE", raising=False)
    analysis_id = _upload_and_analyze()

    for tamper_type in ("input", "policy", "result"):
        response = client.post(f"/api/demo/tamper/{analysis_id}/{tamper_type}")
        assert response.status_code == 404, f"Expected 404 for /tamper/{tamper_type} without DEMO_MODE"


def test_demo_tamper_endpoints_work_with_demo_mode(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    analysis_id = _upload_and_analyze()

    for tamper_type in ("input", "policy", "result"):
        response = client.post(f"/api/demo/tamper/{analysis_id}/{tamper_type}")
        assert response.status_code == 200, f"Expected 200 for /tamper/{tamper_type} with DEMO_MODE=true"
        body = response.json()
        assert body["verification_status"] == "FAILED"
        assert body["mismatch_reason"] is not None
