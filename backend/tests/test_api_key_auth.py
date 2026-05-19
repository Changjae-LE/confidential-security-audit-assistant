import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_SAMPLE = Path(__file__).parents[2] / "samples" / "cloudtrail_suspicious_iam.json"


def test_health_always_open(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "secret-key")
    response = client.get("/health")
    assert response.status_code == 200


def test_endpoints_open_when_api_key_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("API_KEY", raising=False)
    response = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", _SAMPLE.read_bytes(), "application/json")},
    )
    assert response.status_code == 200


def test_correct_api_key_grants_access(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "secret-key")
    response = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", _SAMPLE.read_bytes(), "application/json")},
        headers={"X-API-Key": "secret-key"},
    )
    assert response.status_code == 200


def test_wrong_api_key_returns_401(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "secret-key")
    response = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", _SAMPLE.read_bytes(), "application/json")},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key."


def test_missing_api_key_header_returns_401(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "secret-key")
    response = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", _SAMPLE.read_bytes(), "application/json")},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key."
