# Confidential Security Audit Assistant

Confidential Security Audit Assistant is a hackathon prototype for privacy-preserving security audit analysis. It analyzes uploaded security evidence with deterministic policy rules and an optional AI report enhancement layer, then creates tamper-evident verification metadata.

## Problem

Security audit evidence often contains sensitive data: internal users, asset names, access patterns, cloud configuration details, vulnerability records, and operational logs. Teams want AI-assisted summaries and audit reports, but they also need to avoid exposing raw evidence to public ledgers or unnecessary external systems.

Auditors also need a way to verify that an analysis result was generated from a specific input, policy version, and result set without receiving all raw evidence.

## Solution

The app uploads CSV or JSON evidence, calculates an `input_hash`, runs deterministic security policies, generates findings and a report, and creates a verification record with:

- `input_hash`
- `policy_hash`
- `result_hash`
- `risk_level`
- `compliance_status`
- `verification_status`

Raw evidence stays private in the backend demo store. The public verification record contains hashes and status metadata only.

## Architecture

```text
React Dashboard
  -> FastAPI Backend
    -> Ingestion Agent
    -> Policy Engine
    -> Risk Analysis Agent
    -> Compliance Agent
    -> Report Agent
    -> Verification Agent
    -> Mock Midnight Adapter
```

Current prototype storage is in memory. There is no database yet.

## Tech Stack

- Frontend: React, TypeScript, Tailwind CSS, Vite
- Backend: FastAPI, Pydantic
- Tests: pytest
- Hashing: SHA-256
- Verification: in-memory Mock Midnight adapter
- Optional AI enhancement: OpenAI API if `OPENAI_API_KEY` is set

## AI Agent Workflow

1. `IngestionAgent` normalizes uploaded CSV or JSON evidence.
2. `RiskAnalysisAgent` calls the deterministic Policy Engine.
3. `ComplianceAgent` sets `PASS`, `FAILED`, or `NEEDS_REVIEW`.
4. `ReportAgent` generates deterministic markdown.
5. Optional LLM enhancement may improve wording for summaries and recommendations.

The Policy Engine remains the source of truth. The LLM must not change severity, risk level, compliance status, or verification hashes. If `OPENAI_API_KEY` is missing, the app uses the deterministic report.

## Verification Workflow

1. Uploaded evidence bytes are hashed as `input_hash`.
2. Active policy metadata is hashed as `policy_hash`.
3. Final analysis output is hashed as `result_hash`.
4. The verification record is committed through the mock adapter.
5. Auditor verification recomputes hashes and compares them with the stored record.
6. Tampering returns a failed status with a mismatch reason:
   - `Input hash mismatch`
   - `Policy hash mismatch`
   - `Result hash mismatch`

## Midnight Usage

Midnight integration is currently mocked.

The `MockMidnightAdapter` simulates committing verification records and returns a `mock_tx_id`. It stores only verification metadata in memory. It does not store raw evidence, logs, vulnerability records, internal asset details, or uploaded files.

Planned post-hackathon work is to replace the mock adapter with a real Midnight integration.

## Demo Flow

1. Start the FastAPI backend.
2. Start the React dashboard.
3. Upload sample evidence, such as:
   - `samples/cloudtrail_suspicious_iam.json`
   - `samples/root_login_without_mfa.json`
   - `samples/critical_cve_scan_result.json`
4. Run analysis.
5. Review findings, risk level, compliance status, and report text.
6. Open Auditor Verification and verify the committed record.
7. Open Tamper Detection Demo.
8. Trigger input, policy, or result tampering.
9. Confirm the UI shows verification failure and the mismatch reason.

## Local Setup

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Default local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`

Optional AI report enhancement:

```bash
set OPENAI_API_KEY=your_api_key
```

If the key is not set, the deterministic report is used.

## Backend Tests

```bash
cd backend
pytest
```

Current tests cover upload hashing, policy matching, analysis orchestration, LLM fallback behavior, verification success, and tamper mismatch detection.

## Screenshots

Screenshots placeholder for submission:

- Evidence Upload
- Analysis Results
- Auditor Verification Success
- Tamper Detection Failure

## Roadmap

- Replace in-memory stores with PostgreSQL and private object storage.
- Replace Mock Midnight adapter with real Midnight integration.
- Add immutable policy version records.
- Add PDF export for reports.
- Add organization/workspace support.
- Add role-based access control and authentication.
- Add direct integrations for CloudTrail, vulnerability scanners, and SIEM tools.
- Add human review and approval workflows.
