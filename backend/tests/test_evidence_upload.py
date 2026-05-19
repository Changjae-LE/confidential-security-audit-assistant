import hashlib

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_json_upload_returns_input_hash() -> None:
    content = b'{"eventName":"ConsoleLogin"}'

    response = client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail.json", content, "application/json")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["evidence_id"].startswith("EVD-")
    assert body["filename"] == "cloudtrail.json"
    assert body["content_type"] == "application/json"
    assert body["input_hash"] == hashlib.sha256(content).hexdigest()
    assert body["uploaded_at"]


def test_evidence_ids_are_not_sequential() -> None:
    content = b'{"eventName":"Login"}'

    first = client.post(
        "/api/evidence/upload",
        files={"file": ("a.json", content, "application/json")},
    )
    second = client.post(
        "/api/evidence/upload",
        files={"file": ("b.json", content, "application/json")},
    )

    id_a = first.json()["evidence_id"]
    id_b = second.json()["evidence_id"]
    assert id_a != id_b
    assert id_a.startswith("EVD-")
    assert id_b.startswith("EVD-")
    # Confirm they are not simple increments of each other
    assert id_a[4:] != id_b[4:]


def test_upload_rejects_oversized_file() -> None:
    oversized = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/api/evidence/upload",
        files={"file": ("big.json", oversized, "application/json")},
    )

    assert response.status_code == 413
    assert "10 MB" in response.json()["detail"]


def test_upload_rejects_extension_content_type_mismatch() -> None:
    response = client.post(
        "/api/evidence/upload",
        files={"file": ("evil.json", b'{"x":1}', "application/octet-stream")},
    )

    assert response.status_code == 400


def test_hash_is_consistent_for_same_raw_bytes() -> None:
    content = b"timestamp,event\n2026-05-18,login\n"

    first = client.post(
        "/api/evidence/upload",
        files={"file": ("first.csv", content, "text/csv")},
    )
    second = client.post(
        "/api/evidence/upload",
        files={"file": ("second.csv", content, "text/csv")},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["input_hash"] == second.json()["input_hash"]
    assert first.json()["input_hash"] == hashlib.sha256(content).hexdigest()
