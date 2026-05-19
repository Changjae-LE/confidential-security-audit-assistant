# Demo Flow — Confidential Security Audit Assistant

This document describes the exact steps to run the hackathon demo.
Every step has been verified against the live backend.

---

## Prerequisites

```bash
# Terminal 1 — backend (DEMO_MODE enables the tamper endpoints)
cd backend
pip install -r requirements.txt
DEMO_MODE=true uvicorn app.main:app --reload

# Terminal 2 — frontend (optional, for the UI walkthrough)
cd frontend
npm install
npm run dev        # http://localhost:5173
```

The backend must be running on `http://localhost:8000` before proceeding.

---

## Step 1 — Health check

Confirm the backend is up.

```
GET /health
```

Expected response:

```json
{ "status": "ok" }
```

---

## Step 2 — Upload evidence

Upload `samples/cloudtrail_suspicious_iam.json`.
The file contains two CloudTrail records:
- An IAM privilege escalation (`AttachUserPolicy` → `AdministratorAccess`)
- A root console login without MFA

```
POST /api/evidence/upload
Content-Type: multipart/form-data
Body: file=cloudtrail_suspicious_iam.json (application/json)
```

Expected response shape:

```json
{
  "evidence_id": "EVD-<uuid>",
  "filename": "cloudtrail_suspicious_iam.json",
  "content_type": "application/json",
  "input_hash": "825cbc2a7ba5bb28adfa5bf8c5b3d0b4ac491431e0965faf48f1036cf41f3f5e",
  "uploaded_at": "<ISO-8601 timestamp>"
}
```

`input_hash` is the SHA-256 of the raw uploaded bytes.
It never changes for the same file — you can verify it locally:

```bash
# Linux / macOS
sha256sum samples/cloudtrail_suspicious_iam.json

# Windows PowerShell
Get-FileHash samples\cloudtrail_suspicious_iam.json -Algorithm SHA256
```

Expected SHA-256: `825cbc2a7ba5bb28adfa5bf8c5b3d0b4ac491431e0965faf48f1036cf41f3f5e`

Save `evidence_id` — you need it for the next step.

---

## Step 3 — Run analysis

```
POST /api/analysis/run/{evidence_id}
```

The backend runs the full agent pipeline:

1. **Ingestion Agent** — parses the CloudTrail JSON and normalises each record
2. **Risk Analysis Agent** — evaluates all policy rules against the events
3. **Compliance Agent** — determines `PASS`, `FAILED`, or `NEEDS_REVIEW`
4. **Report Agent** — generates a markdown security audit report
5. **Verification Agent** — computes `input_hash`, `policy_hash`, `result_hash` and commits them to the mock Midnight adapter

Expected response shape:

```json
{
  "analysis_id": "ANL-<uuid>",
  "risk_level": "CRITICAL",
  "compliance_status": "FAILED",
  "findings": [ ... ],
  "report": "# Security Audit Report: ANL-...",
  "verification_record": { ... }
}
```

Save `analysis_id` — you need it for steps 5–7.

---

## Step 4 — Findings and report

The analysis returns two findings for the CloudTrail sample:

### Finding 1 — Root account login without MFA

```
rule_id  : POL-ROOT-MFA-001
severity : Critical
asset    : AWS root account
summary  : A root console login succeeded without MFA.
action   : Investigate the root login and require MFA for root account access.
score    : 0.98
```

### Finding 2 — Suspicious IAM privilege escalation

```
rule_id  : POL-IAM-PRIV-001
severity : High
asset    : alice
summary  : An IAM change granted or attempted to grant broad administrative privileges.
action   : Review the IAM change, revoke excessive permissions, and rotate affected credentials if needed.
score    : 0.92
```

### Report structure

```
# Security Audit Report: ANL-<uuid>

- Risk Level: CRITICAL
- Compliance Status: FAILED
- Finding Count: 2

## Findings
### Root account login without MFA
...
### Suspicious IAM privilege escalation
...
```

If `OPENAI_API_KEY` is set, a `## LLM-Enhanced Executive Summary` section is appended.
If the key is absent, the deterministic report is returned as-is.

---

## Step 5 — View verification record

```
GET /api/verification/{analysis_id}
```

This returns the record committed to the mock Midnight adapter during analysis.

Expected response shape:

```json
{
  "analysis_id": "ANL-<uuid>",
  "mock_tx_id": "MOCK-MIDNIGHT-<12 hex chars>",
  "verification_status": "COMMITTED",
  "committed_at": "<ISO-8601 timestamp>",
  "input_hash": "825cbc2a7ba5bb28adfa5bf8c5b3d0b4ac491431e0965faf48f1036cf41f3f5e",
  "policy_hash": "fe5d6f82addb81acf77912b2e65e4367d3a36c1713561983131a531bdde76bf8",
  "result_hash": "<SHA-256 of canonical analysis result>",
  "risk_level": "CRITICAL",
  "compliance_status": "FAILED"
}
```

`policy_hash` is deterministic — it is the SHA-256 of the policy rule set definition and will be the same for every run against the same policy version:

```
fe5d6f82addb81acf77912b2e65e4367d3a36c1713561983131a531bdde76bf8
```

`result_hash` varies per run because it covers the full analysis result (findings, risk level, compliance status, report text, and the analysis ID).

---

## Step 6 — Verify integrity (clean evidence)

Re-run the hash comparison against the committed record.

```
POST /api/verification/{analysis_id}/verify
```

Expected response:

```json
{
  "analysis_id": "ANL-<uuid>",
  "verification_status": "VERIFIED",
  "mismatch_reason": null,
  "input_hash_match": true,
  "policy_hash_match": true,
  "result_hash_match": true,
  "record": { ... }
}
```

All three hashes match the committed record. `verification_status` is `VERIFIED`.

---

## Step 7 — Tamper detection

Simulate an attacker modifying the evidence after analysis.
The demo endpoint replaces the stored evidence bytes with empty records without changing the committed Midnight hashes.

```
POST /api/demo/tamper/{analysis_id}/input
```

> This endpoint requires `DEMO_MODE=true` in the backend environment.
> Without it the endpoint returns 404.

Expected response:

```json
{
  "analysis_id": "ANL-<uuid>",
  "verification_status": "FAILED",
  "mismatch_reason": "Input hash mismatch",
  "input_hash_match": false,
  "policy_hash_match": true,
  "result_hash_match": true,
  "record": { ... }
}
```

`input_hash_match` is `false` because the stored evidence bytes were replaced.
The committed `input_hash` in the Midnight record no longer matches the current bytes.
`verification_status` is `FAILED`.

Two other tamper variants are also available:

| Endpoint | Simulates | Expected mismatch |
|---|---|---|
| `POST /api/demo/tamper/{id}/input` | Evidence bytes modified | `Input hash mismatch` |
| `POST /api/demo/tamper/{id}/policy` | Policy version swapped | `Policy hash mismatch` |
| `POST /api/demo/tamper/{id}/result` | Analysis result modified | `Result hash mismatch` |

---

## Running the full flow from the CLI

The demo script at `backend/scripts/demo_tamper_detection.py` runs all 7 steps
in-process (no server required) and prints pass/fail for each:

```bash
cd backend
python scripts/demo_tamper_detection.py
```

---

## What the demo proves

| Claim | Evidence |
|---|---|
| Raw evidence is never exposed | `/api/analysis/run` returns findings, not raw log lines |
| Evidence integrity is verifiable | `input_hash` in the Midnight record matches `sha256(uploaded_file)` |
| Policy is version-pinned | `policy_hash` is deterministic across runs for the same rule set |
| Analysis result is tamper-evident | `result_hash` covers findings, risk level, compliance status, and report |
| Tampering is detected | Modifying any of the three sources changes the hash and fails verification |
| LLM does not decide severity | Policy engine runs first; LLM only rewrites report prose |

---

## Known limitations (demo scope)

- All state is in-memory. A backend restart clears all evidence, analyses, and verification records.
- The Midnight adapter is mocked (`mock_tx_id`). A real Midnight integration would make the committed hashes immutable on-chain.
- No authentication is implemented. All endpoints are open. Do not expose this to the internet.
- File uploads are limited to 10 MB. Only `.json` and `.csv` are accepted.
