# AGENTS.md

## Purpose

Repository instructions for Codex.

This file is not a README. Keep changes focused, secure, and testable when working on Confidential Security Audit Assistant.

## Project Rule

Confidential Security Audit Assistant analyzes sensitive security evidence with FastAPI, AI Agents, a policy engine, private storage, PostgreSQL, and Midnight verification records.

Raw evidence must stay private. Midnight must store only verification metadata.

## Core Security Rules

- Never store raw security evidence on Midnight.
- Never include raw logs, CloudTrail events, vulnerability scan files, web access logs, internal IPs, usernames, system names, or asset details in public verification records.
- Do not expose raw uploaded evidence in normal API responses.
- Do not log raw evidence content.
- Do not hardcode secrets.
- Use environment variables for API keys, database URLs, and Midnight configuration.
- Validate uploaded file type and file size.
- Sanitize uploaded filenames.

## Verification Rules

- Use SHA-256 for `input_hash`, `policy_hash`, and `result_hash`.
- Generate `input_hash` from the original uploaded evidence.
- Generate `policy_hash` from the active policy version.
- Generate `result_hash` from the final analysis result.
- Verification succeeds only when recalculated hashes match the stored verification record.
- If uploaded evidence changes, return `Input hash mismatch`.
- If the policy changes, return `Policy hash mismatch`.
- If the analysis result changes, return `Result hash mismatch`.

Verification records should contain:

```json
{
  "analysis_id": "ANL-2026-0001",
  "input_hash": "hash_of_original_evidence",
  "policy_hash": "hash_of_policy_version",
  "result_hash": "hash_of_analysis_result",
  "risk_level": "HIGH",
  "compliance_status": "FAILED",
  "verification_status": "COMMITTED"
}
```

## AI and Policy Rules

- The policy engine must run before AI reasoning.
- The LLM must not be the only source of security judgment.
- AI Agents should explain, summarize, and enrich policy results.
- Severity should be grounded in policy evidence when possible.
- If evidence is insufficient, use `NEEDS_REVIEW` instead of guessing.
- Do not claim that AI analysis is always correct.
- Do not claim that this system replaces human security audits.

## Initial Policies

Implement these policies first:

1. Root account login without MFA = Critical
2. IAM privilege escalation = High
3. Public S3 bucket = High
4. Security group open to `0.0.0.0/0` = High
5. Critical CVE with CVSS >= 9.0 = Critical
6. Web attack followed by HTTP 500 error = High

Each policy result should include `rule_id`, `title`, `severity`, `matched_evidence`, `affected_asset`, `explanation`, and `recommended_action`.

## Backend Rules

- Use FastAPI for backend APIs.
- Keep `main.py` minimal.
- Do not put business logic directly inside route handlers.
- Route handlers must call services.
- Use Pydantic schemas for request and response validation.
- Use SQLAlchemy models for database entities.
- Use PostgreSQL for metadata.
- Use private storage for uploaded evidence.
- Put API routes under `backend/app/api/`.
- Put reusable business logic under `backend/app/services/`.
- Put policy logic under `backend/app/policies/`.
- Put AI Agent logic under `backend/app/agents/`.

## Frontend Rules

- Use React, TypeScript, and Tailwind CSS.
- Build views for upload, findings, reports, auditor verification, and tamper detection.
- Do not expose raw evidence unnecessarily in the UI.

## Required Commands

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run lint
```

Docker:

```bash
docker compose up --build
```

## Testing Expectations

After backend changes, run:

```bash
cd backend
pytest
```

After frontend changes, run:

```bash
cd frontend
npm run lint
```

Add or update tests when changing hashing, verification, policy matching, or tamper detection.

Minimum tests should cover evidence hashing, policy matching, verification success, input hash mismatch, policy hash mismatch, and result hash mismatch.

## Definition of Done

A task is done only when:

- The requested behavior is implemented.
- Relevant tests or checks have been run.
- Security-sensitive data is not exposed.
- The policy engine remains the first source of security judgment.
- Hash verification still works.
- The diff does not include unrelated changes.

## Do Not Do

- Do not write a long README-style explanation here.
- Do not store raw evidence on Midnight.
- Do not let the LLM decide severity without policy evidence.
- Do not put all logic in `main.py`.
- Do not expose raw logs in API responses.
- Do not log uploaded file contents.
- Do not hardcode secrets.
- Do not skip tamper detection.
- Do not modify unrelated files when implementing a requested feature.
