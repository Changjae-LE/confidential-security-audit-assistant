# PRD: Confidential Security Audit Assistant

## 1. Product Overview

**Product Name:** Confidential Security Audit Assistant  
**Track:** Midnight Hackathon — AI Track

Confidential Security Audit Assistant is a privacy-preserving AI security audit platform that helps enterprises analyze sensitive security logs, cloud configuration data, and vulnerability scan results without exposing raw data. After the analysis, the system creates a verifiable audit record through Midnight so that users and auditors can validate the integrity of the input evidence, policy version, and analysis results.

## 2. Problem

Enterprises want to use AI to analyze security logs and vulnerability reports, but raw evidence often contains sensitive information such as internal IP addresses, user accounts, system names, access patterns, permission structures, and vulnerable assets.

AI-generated security reports also create trust and auditability challenges:

- It is difficult to verify which original evidence was used to generate the report.
- It is difficult to trace which security policy or rule version was applied.
- It is difficult to prove that the analysis result was not modified after generation.
- Auditors often need evidence, but sharing full raw logs can expose sensitive internal data.

## 3. Solution

Confidential Security Audit Assistant performs AI-based security analysis without exposing raw security data. Instead of publishing the original logs, the system records only the key verification values generated during the analysis process.

```text
Raw Security Logs -> AI Analysis -> Security Findings
                          |
                          v
Input Hash + Policy Hash + Result Hash
                          |
                          v
Midnight Verification Record
```

With this approach, an auditor can verify the following without viewing the full raw logs:

- The analysis was performed using a specific input evidence set.
- A specific policy version was used during analysis.
- The analysis result was not modified after generation.
- The compliance status is one of Pass, Failed, or Needs Review.

## 4. Target Users

| User                    | Main Need                                                                |
| ----------------------- | ------------------------------------------------------------------------ |
| SOC Analyst             | Quickly identify risky events from security logs                         |
| Compliance Auditor      | Verify the integrity of analysis results without accessing full raw logs |
| Security Manager / CISO | Review overall risk status and audit-ready reports                       |
| Cloud Security Engineer | Analyze IAM, CloudTrail, cloud configuration, and vulnerability findings |

## 5. Core Features

### 5.1 Evidence Upload

Users can upload security logs or vulnerability scan results.

Supported initial data types:

- CSV
- JSON
- CloudTrail-style JSON
- Vulnerability scan results
- Web access logs

The system generates a hash of the uploaded file and stores the raw evidence in private storage.

### 5.2 AI Risk Analysis

AI agents analyze the uploaded data and generate security findings.

Each finding includes:

- Finding title
- Severity
- Evidence summary
- Affected asset
- Reasoning
- Recommended action
- Confidence score

Example finding:

```json
{
  "title": "Suspicious IAM Privilege Escalation",
  "severity": "High",
  "evidence_summary": "An unusual administrator attached a high-privilege policy to a production role.",
  "recommended_action": "Review the IAM change and revoke unnecessary permissions."
}
```

### 5.3 Policy-Based Detection

The system does not rely entirely on the LLM for security decisions. A rule engine performs the initial detection and severity classification, while AI agents generate explanations, summaries, and reports.

Initial policy examples:

1. Root account login without MFA = Critical
2. IAM privilege escalation = High
3. Public S3 bucket = High
4. Security group open to `0.0.0.0/0` = High
5. Critical CVE with CVSS >= 9.0 = Critical
6. Web attack followed by HTTP 500 error = High

### 5.4 Report Generation

The system generates three types of reports:

1. SOC Analyst Report
2. Executive Summary Report
3. Auditor Verification Report

Reports include risk level, key findings, recommended actions, compliance status, and verification record details.

### 5.5 Midnight Verification Record

After the analysis is completed, the system generates the following values and records them through Midnight.

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

The most important design principle is that raw logs are never stored on Midnight. Midnight stores only verifiable hashes and status values, not the original security evidence.

### 5.6 Auditor Verification

Auditors can use the Auditor View to inspect verification metadata.

Auditor-visible fields include:

- Analysis ID
- Timestamp
- Input Hash
- Policy Hash
- Result Hash
- Risk Level
- Compliance Status
- Midnight Verification Status

This allows auditors to verify that the analysis result has not been tampered with, without requiring access to the full raw logs.

### 5.7 Tamper Detection

If the original log, policy, or analysis result is modified, the newly calculated hash will no longer match the hash recorded in the verification record.

Example output:

```text
Verification Failed
Reason: Input hash mismatch
```

This is the core demo moment for the hackathon because it clearly shows privacy-preserving and tamper-evident auditability.

## 6. AI Agent Architecture

The product uses five AI agents.

| Agent               | Role                                                                            |
| ------------------- | ------------------------------------------------------------------------------- |
| Ingestion Agent     | Parse and normalize uploaded log files                                          |
| Risk Analysis Agent | Detect risky events and assign severity                                         |
| Compliance Agent    | Determine policy violations and compliance status                               |
| Report Agent        | Generate user-specific reports                                                  |
| Verification Agent  | Generate hashes, commit verification records, and process verification requests |

## 7. System Architecture

```text
[React Dashboard]
        |
        v
[FastAPI Backend]
        |
        v
[AI Agent Orchestrator]
        |
        v
[Policy Engine + Report Service + Verification Service]
        |
        v
[PostgreSQL + Private Storage]
        |
        v
[Midnight Verification Record]
```

Recommended technology stack:

| Layer        | Technology                                   |
| ------------ | -------------------------------------------- |
| Frontend     | React, TypeScript, Tailwind CSS              |
| Backend      | FastAPI, Pydantic, SQLAlchemy                |
| Database     | PostgreSQL                                   |
| AI           | LangGraph or CrewAI, OpenAI API or local LLM |
| Verification | SHA-256 hash, Midnight Adapter               |

## 8. Trust Model

### 8.1 What the System Proves

The system can prove that:

- The analysis was performed using a specific input evidence set.
- The input evidence has not changed since analysis.
- A specific policy version was used for the analysis.
- The analysis result has not been modified after generation.
- A verifiable record exists through Midnight.

### 8.2 What the System Does Not Prove

The system does not prove that:

- The AI judgment is always 100% correct.
- Every possible attack was detected.
- Every compliance requirement was fully satisfied.
- Human security auditors can be fully replaced.

## 9. Demo Flow

The hackathon demo follows this flow:

1. The user uploads a sample CloudTrail log.
2. The FastAPI backend stores the file and generates an `input_hash`.
3. AI agents analyze the log and identify risky events.
4. The system generates findings and reports.
5. The Verification Agent generates `input_hash`, `policy_hash`, and `result_hash`.
6. The system creates a Midnight verification record.
7. The Auditor View shows successful verification.
8. The original log is modified.
9. The system runs verification again and shows an `input_hash mismatch` failure.

## 10. Success Criteria

Hackathon submission success criteria:

- Users can upload security logs.
- AI agents generate security findings.
- Findings include severity, evidence summary, and recommended action.
- The system generates `input_hash`, `policy_hash`, and `result_hash`.
- The system creates a Midnight verification record.
- The Auditor View shows successful verification.
- Tampered logs cause verification failure.

## 11. Roadmap

### 11.1 Hackathon Version

- React dashboard
- FastAPI backend
- CSV/JSON upload
- CloudTrail sample support
- 5 to 8 initial security policy rules
- AI agent-based analysis
- Report generation
- Hash-based verification
- Mock or initial Midnight adapter
- Auditor View
- Tamper Detection Demo

### 11.2 Post-Hackathon Version

- Real Midnight Compact smart contract integration
- Splunk API integration
- Direct AWS CloudTrail integration
- Semgrep, Trivy, and OSV-Scanner integration
- PDF report export
- Multi-tenant organization support
- Role-based access control
- SSO/OIDC support

### 11.3 Enterprise Version

- On-prem deployment
- Customer-managed encryption keys
- SIEM/SOAR integration
- Human-in-the-loop review
- Approval workflow
- Selective disclosure
- ZK-based claim verification
- SOC 2, ISO 27001, and NIST CSF mapping

## 12. Final Summary

Confidential Security Audit Assistant helps enterprises use AI for security audits without exposing sensitive security data.

The core values are:

**AI Usefulness:**  
The system quickly analyzes security logs and vulnerability data and generates audit-ready reports.

**Privacy:**  
Raw security data is not exposed to auditors, external services, or the public ledger.

**Verifiable Trust:**  
The system records hashes of the input evidence, policy version, and analysis result through Midnight so that auditors can verify the integrity of the result.

## 13. Presentation Summary

> Confidential Security Audit Assistant helps enterprises analyze sensitive security logs with AI without exposing raw data, while using Midnight to make the evidence, policy version, and analysis results tamper-evident and verifiable.
