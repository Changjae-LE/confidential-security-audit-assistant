# TRD: Confidential Security Audit Assistant

## 1. Overview

**Product Name:** Confidential Security Audit Assistant  
**Track:** Midnight Hackathon — AI Track  
**Goal:** Analyze sensitive security evidence with AI without exposing raw data, then create verifiable integrity records using Midnight.

The system allows users to upload security logs, cloud configuration data, and vulnerability scan results. The backend analyzes the data using a rule-based policy engine and AI agents, generates security findings and reports, and stores verification hashes on Midnight instead of storing raw logs publicly.

---

## 2. Core Objectives

The system must support:

1. Evidence upload for CSV, JSON, CloudTrail-style JSON, vulnerability scan results, and web access logs.
2. SHA-256 hash generation for uploaded evidence.
3. Rule-based security detection using predefined policies.
4. AI Agent-based risk explanation and report generation.
5. Compliance status calculation: `PASS`, `FAILED`, or `NEEDS_REVIEW`.
6. Verification record creation using `input_hash`, `policy_hash`, and `result_hash`.
7. Midnight commit or mock Midnight verification record.
8. Auditor View for verification without exposing raw logs.
9. Tamper detection when evidence, policy, or result data changes.

---

## 3. System Architecture

```text
[React Dashboard]
        ↓
[FastAPI Backend]
        ↓
[AI Agent Orchestrator]
        ↓
[Policy Engine + Report Service + Verification Service]
        ↓
[PostgreSQL + Private Storage]
        ↓
[Midnight Adapter]
        ↓
[Midnight Verification Record]
```

---

## 4. Technology Stack

| Layer        | Technology                                                           |
| ------------ | -------------------------------------------------------------------- |
| Frontend     | React, TypeScript, Tailwind CSS                                      |
| Backend      | FastAPI, Pydantic, SQLAlchemy                                        |
| Database     | PostgreSQL                                                           |
| File Storage | Local private storage for demo; S3-compatible storage for production |
| AI Agent     | LangGraph or CrewAI                                                  |
| LLM          | OpenAI API or local LLM                                              |
| Verification | SHA-256, Midnight Adapter                                            |
| Deployment   | Docker, Docker Compose                                               |

---

## 5. Core Components

### 5.1 React Dashboard

The frontend provides:

- Evidence upload page
- Analysis result page
- Report view
- Auditor verification view
- Tamper detection demo page

### 5.2 FastAPI Backend

The backend handles:

- File upload
- Hash generation
- Analysis job creation
- Agent orchestration
- Policy evaluation
- Report generation
- Verification record management

### 5.3 AI Agent Orchestrator

The system uses multiple agents:

| Agent               | Responsibility                                 |
| ------------------- | ---------------------------------------------- |
| Ingestion Agent     | Parse and normalize uploaded evidence          |
| Risk Analysis Agent | Generate security findings from policy matches |
| Compliance Agent    | Determine compliance status                    |
| Report Agent        | Generate SOC, executive, and auditor reports   |
| Verification Agent  | Generate hashes and verify records             |

### 5.4 Policy Engine

The Policy Engine performs deterministic detection before AI explanation. AI should not be the only source of security judgment.

Initial rules:

| Rule                               | Severity |
| ---------------------------------- | -------- |
| Root account login without MFA     | Critical |
| IAM privilege escalation           | High     |
| Public S3 bucket                   | High     |
| Security group open to `0.0.0.0/0` | High     |
| Critical CVE with CVSS >= 9.0      | Critical |
| Web attack followed by 500 error   | High     |

### 5.5 Verification Service

The Verification Service generates:

```text
input_hash = SHA256(original evidence file)
policy_hash = SHA256(policy version)
result_hash = SHA256(canonical analysis result)
```

Only hashes and status values are committed to Midnight. Raw logs must never be stored on Midnight.

---

## 6. Main API Requirements

### 6.1 Upload Evidence

```http
POST /api/evidence/upload
```

Uploads evidence and returns an `evidence_id` and `input_hash`.

Response example:

```json
{
  "evidence_id": "EVD-2026-0001",
  "filename": "cloudtrail_sample.json",
  "evidence_type": "cloudtrail",
  "input_hash": "sha256_hash_value",
  "storage_status": "STORED"
}
```

### 6.2 Start Analysis

```http
POST /api/analysis/start
```

Starts an analysis job for a specific evidence file and policy version.

Request example:

```json
{
  "evidence_id": "EVD-2026-0001",
  "policy_version": "policy-v1.0.0"
}
```

### 6.3 Get Analysis Result

```http
GET /api/analysis/{analysis_id}
```

Returns findings, risk level, and compliance status.

### 6.4 Generate Report

```http
POST /api/reports/generate
```

Supported report types:

- `soc`
- `executive`
- `auditor`

### 6.5 Commit Verification Record

```http
POST /api/verification/commit
```

Creates a verification record and commits it to Midnight or the mock Midnight adapter.

### 6.6 Recheck Verification

```http
POST /api/verification/recheck
```

Recalculates hashes and compares them against the committed verification record.

If evidence was modified, the system should return:

```json
{
  "verification_result": "INVALID",
  "reason": "Input hash mismatch"
}
```

---

## 7. Data Model

### 7.1 evidence_files

Stores uploaded evidence metadata.

Required fields:

- `evidence_id`
- `filename`
- `evidence_type`
- `storage_path`
- `input_hash`
- `created_at`

### 7.2 analysis_jobs

Stores analysis job status.

Required fields:

- `analysis_id`
- `evidence_id`
- `policy_version`
- `status`
- `risk_level`
- `compliance_status`
- `created_at`
- `completed_at`

### 7.3 findings

Stores security findings.

Required fields:

- `finding_id`
- `analysis_id`
- `title`
- `severity`
- `affected_asset`
- `evidence_summary`
- `reasoning`
- `recommended_action`
- `confidence_score`

### 7.4 reports

Stores generated reports.

Required fields:

- `report_id`
- `analysis_id`
- `report_type`
- `content`
- `result_hash`

### 7.5 verification_records

Stores verification metadata.

Required fields:

- `verification_id`
- `analysis_id`
- `input_hash`
- `policy_hash`
- `result_hash`
- `risk_level`
- `compliance_status`
- `midnight_record_id`
- `verification_status`

---

## 8. Security Requirements

The system must:

1. Store raw evidence only in private storage.
2. Never store raw logs on Midnight.
3. Use SHA-256 hashing for integrity verification.
4. Avoid sending full raw logs to the LLM.
5. Send only normalized and necessary evidence fields to AI agents.
6. Validate AI output with Pydantic schemas.
7. Keep policy versions immutable after use.
8. Record all major actions in audit logs.

---

## 9. AI Safety Requirements

The AI layer must:

1. Use Policy Engine results as the primary evidence source.
2. Generate explanations only from provided evidence.
3. Avoid unsupported claims.
4. Mark AI-only findings as `NEEDS_REVIEW`.
5. Prevent prompt injection from uploaded logs.
6. Return structured output that matches backend schemas.

---

## 10. Verification Flow

```text
1. User uploads evidence.
2. Backend calculates input_hash.
3. Policy Engine evaluates evidence.
4. AI Agents generate findings and reports.
5. Backend calculates policy_hash and result_hash.
6. Verification Agent creates a verification record.
7. Midnight Adapter commits the record.
8. Auditor checks the verification record.
9. If the evidence is modified, recheck detects hash mismatch.
```

---

## 11. Demo Flow

The hackathon demo should show:

1. Upload CloudTrail sample log.
2. Generate `input_hash`.
3. Run AI analysis.
4. Detect suspicious IAM activity.
5. Generate a High severity finding.
6. Generate compliance status as `FAILED`.
7. Commit verification record.
8. Show verification success in Auditor View.
9. Modify the original evidence.
10. Recheck verification.
11. Show `Input hash mismatch`.

---

## 12. Deployment Requirements

### Local Development

Use Docker Compose with:

- React frontend
- FastAPI backend
- PostgreSQL
- Local private storage
- Mock Midnight adapter

### Production Direction

Future production deployment should support:

- Real Midnight integration
- Encrypted object storage
- RBAC
- SSO/OIDC
- Multi-tenant organization support
- SIEM/SOAR integration
- Splunk and AWS CloudTrail integration
- PDF report export
- Human review workflow

---

## 13. Testing Requirements

Required tests:

1. File upload test
2. SHA-256 hash generation test
3. Policy matching test
4. AI output schema validation test
5. Compliance status calculation test
6. Report generation test
7. Verification commit test
8. Tamper detection test

---

## 14. Acceptance Criteria

The system is considered complete when:

1. Users can upload CSV or JSON security evidence.
2. The system generates an `input_hash`.
3. The Policy Engine detects at least five security rule types.
4. AI Agents generate findings with severity, evidence, reasoning, and recommendation.
5. The system calculates compliance status.
6. The system generates SOC, executive, and auditor reports.
7. The system creates `input_hash`, `policy_hash`, and `result_hash`.
8. The system creates a Midnight verification record.
9. Auditor View shows verification status.
10. Tampered evidence causes verification failure.
11. Raw logs are never stored on Midnight.

---

## 15. Final Technical Direction

The project should be implemented as a security audit platform where:

- The Policy Engine performs deterministic detection.
- AI Agents explain findings and generate reports.
- The Verification Service proves integrity using hashes.
- Midnight provides an externally verifiable audit record.
- Auditor View verifies results without exposing raw evidence.

This structure fits the AI Track while keeping the project practical for post-hackathon enterprise expansion.
