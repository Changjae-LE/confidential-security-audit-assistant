"""
Tamper detection demo.

Runs entirely in-process via TestClient so no server needs to be running.
Steps:
  1. Upload cloudtrail_suspicious_iam.json
  2. Run analysis
  3. Verify  -> VERIFIED
  4. Mutate the stored evidence bytes (simulate tamper)
  5. Re-verify -> FAILED / Input hash mismatch
"""

import json
import sys
from pathlib import Path

# Ensure 'backend/' is on the path when run as a script.
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.evidence_service import replace_evidence_content  # noqa: E402

SAMPLE = (
    Path(__file__).parent.parent.parent / "samples" / "cloudtrail_suspicious_iam.json"
)

client = TestClient(app)


def _check(response, label: str) -> dict:
    if response.status_code not in (200, 201):
        print(f"  [ERROR] {label} -> HTTP {response.status_code}: {response.text}")
        sys.exit(1)
    return response.json()


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ── Step 1: Upload ────────────────────────────────────────────
section("STEP 1 - Upload evidence")

raw_bytes = SAMPLE.read_bytes()
upload = _check(
    client.post(
        "/api/evidence/upload",
        files={"file": ("cloudtrail_suspicious_iam.json", raw_bytes, "application/json")},
    ),
    "upload",
)
evidence_id = upload["evidence_id"]
input_hash = upload["input_hash"]
print(f"  evidence_id : {evidence_id}")
print(f"  input_hash  : {input_hash}")

# ── Step 2: Run analysis ──────────────────────────────────────
section("STEP 2 - Run analysis")

analysis = _check(
    client.post(f"/api/analysis/run/{evidence_id}"),
    "analysis",
)
analysis_id = analysis["analysis_id"]
print(f"  analysis_id       : {analysis_id}")
print(f"  risk_level        : {analysis['risk_level']}")
print(f"  compliance_status : {analysis['compliance_status']}")
print(f"  findings ({len(analysis['findings'])}):")
for f in analysis["findings"]:
    print(f"    [{f['severity']}] {f['title']}")

vr = analysis["verification_record"]
print(f"\n  verification_record:")
print(f"    mock_tx_id  : {vr['mock_tx_id']}")
print(f"    input_hash  : {vr['input_hash']}")
print(f"    policy_hash : {vr['policy_hash']}")
print(f"    result_hash : {vr['result_hash']}")

# ── Step 3: Verify (clean) ────────────────────────────────────
section("STEP 3 - Verify (original evidence, expect VERIFIED)")

result = _check(
    client.post(f"/api/verification/{analysis_id}/verify"),
    "verify",
)
print(f"  verification_status : {result['verification_status']}")
print(f"  input_hash_match    : {result['input_hash_match']}")
print(f"  policy_hash_match   : {result['policy_hash_match']}")
print(f"  result_hash_match   : {result['result_hash_match']}")
print(f"  mismatch_reason     : {result['mismatch_reason']}")

if result["verification_status"] != "VERIFIED":
    print("  [ERROR] Expected VERIFIED but got:", result["verification_status"])
    sys.exit(1)
print("  OK - clean verification passed.")

# ── Step 4: Tamper with the evidence ─────────────────────────
section("STEP 4 - Tamper with evidence (mutate stored bytes)")

original_json = json.loads(raw_bytes)
original_json["Records"][0]["sourceIPAddress"] = "10.0.0.1-TAMPERED"
tampered_bytes = json.dumps(original_json).encode()

replace_evidence_content(evidence_id, tampered_bytes)
print(f"  Original  bytes : {len(raw_bytes)} bytes, hash {input_hash[:16]}...")
import hashlib  # noqa: E402
tampered_hash = hashlib.sha256(tampered_bytes).hexdigest()
print(f"  Tampered  bytes : {len(tampered_bytes)} bytes, hash {tampered_hash[:16]}...")
print("  Stored evidence replaced with tampered copy.")

# ── Step 5: Re-verify (tampered) ─────────────────────────────
section("STEP 5 - Re-verify (tampered evidence, expect FAILED)")

tampered_result = _check(
    client.post(f"/api/verification/{analysis_id}/verify"),
    "re-verify",
)
print(f"  verification_status : {tampered_result['verification_status']}")
print(f"  input_hash_match    : {tampered_result['input_hash_match']}")
print(f"  policy_hash_match   : {tampered_result['policy_hash_match']}")
print(f"  result_hash_match   : {tampered_result['result_hash_match']}")
print(f"  mismatch_reason     : {tampered_result['mismatch_reason']}")

if tampered_result["mismatch_reason"] != "Input hash mismatch":
    print("  [ERROR] Expected 'Input hash mismatch', got:", tampered_result["mismatch_reason"])
    sys.exit(1)

# ── Summary ───────────────────────────────────────────────────
section("DEMO COMPLETE")
print("  Clean verification  : VERIFIED")
print("  Tampered verification: FAILED - Input hash mismatch")
print("  Tamper detection is working correctly.\n")
