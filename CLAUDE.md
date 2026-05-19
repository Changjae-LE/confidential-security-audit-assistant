# CLAUDE.md

## Purpose

This is not a README. It is a guardrail file for Claude Code.
Use it to avoid repeated mistakes while building Confidential Security Audit Assistant.

## Core Rules

- Raw security evidence must stay private.
- Never store raw logs, CloudTrail events, vulnerability scan files, web access logs, internal IPs, usernames, system names, or asset details on Midnight.
- Midnight stores only verification metadata.
- The trust model is hash-based integrity verification, not public disclosure of raw evidence.
- Do not claim the AI is always correct or that this replaces a human audit.

## Verification Rules

- Use SHA-256 for `input_hash`, `policy_hash`, and `result_hash`.
- `input_hash` comes from the original uploaded evidence.
- `policy_hash` comes from the active policy version.
- `result_hash` comes from the final analysis result.
- Verification succeeds only when recalculated hashes match the stored record.
- Evidence change => `Input hash mismatch`.
- Policy change => `Policy hash mismatch`.
- Result change => `Result hash mismatch`.
- Verification records may include `analysis_id`, `input_hash`, `policy_hash`, `result_hash`, `risk_level`, `compliance_status`, `verification_status`, and `timestamp`.

## AI and Policy Rules

- The policy engine must run before AI reasoning.
- The LLM must not be the only source of security judgment.
- AI Agents explain, summarize, and enrich policy results.
- Severity should be grounded in policy evidence.
- If evidence is insufficient, use `NEEDS_REVIEW` instead of guessing.

## Initial Detection Policies

1. Root account login without MFA = Critical
2. IAM privilege escalation = High
3. Public S3 bucket = High
4. Security group open to `0.0.0.0/0` = High
5. Critical CVE with CVSS >= 9.0 = Critical
6. Web attack followed by HTTP 500 error = High

Each policy result should include `rule_id`, `title`, `severity`, `matched_evidence`, `affected_asset`, `explanation`, and `recommended_action`.

## Agent Boundaries

- Ingestion Agent: parse uploaded files and normalize evidence.
- Risk Analysis Agent: detect risky events and assign severity using policy results.
- Compliance Agent: determine `PASS`, `FAILED`, or `NEEDS_REVIEW`.
- Report Agent: generate SOC, executive, and auditor reports.
- Verification Agent: generate hashes, create verification records, and validate tamper detection.

Do not merge all agent logic into one large function.

## Backend Rules

- Use FastAPI for backend APIs.
- Do not put business logic directly inside route handlers.
- Route handlers must call services.
- Use Pydantic schemas for request and response validation.
- Use SQLAlchemy models for database entities.
- Use PostgreSQL for metadata.
- Use private storage for uploaded evidence.
- Do not return or log raw evidence in normal API behavior.

## Frontend Rules

- Use React, TypeScript, and Tailwind CSS.
- Build upload, findings, reports, auditor verification, and tamper detection views.
- Do not expose raw evidence unnecessarily in the UI.

## Security Rules

- Validate uploaded file type and size.
- Sanitize uploaded filenames.
- Do not hardcode secrets.
- Use environment variables for API keys, database URLs, and Midnight configuration.
- Keep auditor-facing verification data separate from analyst/admin data.

## Required Commands

- Backend setup: `cd backend && pip install -r requirements.txt`
- Backend run: `cd backend && uvicorn app.main:app --reload`
- Backend test: `cd backend && pytest`
- Frontend setup: `cd frontend && npm install`
- Frontend run: `cd frontend && npm run dev`
- Frontend lint: `cd frontend && npm run lint`
- Docker run: `docker compose up --build`

## Implementation Order

File upload API → hashing service → private storage → policy engine → AI orchestration → findings → reports → verification record → auditor verification API → tamper detection demo → React dashboard → Midnight adapter.

## Do Not Do

- Do not write README-style product explanations here.
- Do not store raw evidence on Midnight.
- Do not let the LLM decide severity without policy evidence.
- Do not put all logic in `main.py` or FastAPI routes.
- Do not expose raw logs in API responses.
- Do not log uploaded file contents.
- Do not hardcode secrets.
- Do not skip tamper detection.
- Do not modify unrelated files.
