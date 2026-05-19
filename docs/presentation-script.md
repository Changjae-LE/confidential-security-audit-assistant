# Presentation Script — Confidential Security Audit Assistant
## 3-Minute Hackathon Demo

*Format: speaker notes with [ACTION] cues for what to do on screen at each step.*
*Timing targets are listed per section. Aim to reach tamper detection by the 2:00 mark.*

---

## Pitch (0:00 – 0:15)

**Say:**
> "Confidential Security Audit Assistant analyzes sensitive security logs with AI, generates tamper-evident findings, and lets any auditor verify the result — without ever seeing the raw evidence."

---

## Problem (0:15 – 0:35)

**Say:**
> "Security audit evidence is sensitive. CloudTrail logs contain usernames, internal IPs, asset names, and access patterns. When teams want AI-assisted summaries, the obvious move is to pipe that raw data into a language model — but that creates a privacy and compliance risk. On top of that, auditors reviewing findings have no way to know whether the evidence was changed after the analysis was run."

---

## Solution (0:35 – 0:55)

**Say:**
> "Our approach: raw evidence never leaves the backend. Instead, we hash it. A deterministic policy engine evaluates the evidence first. AI agents enrich the output. A verification record — containing only hashes and status metadata, never raw logs — is committed to a tamper-evident store. Any auditor can re-run verification at any time and get a pass or fail with a specific mismatch reason."

---

## Live Demo (0:55 – 2:15)

### Step 1 — Upload evidence (0:55 – 1:10)

[ACTION: Open the React dashboard at http://localhost:5173. Navigate to the Upload view. Drop in `samples/cloudtrail_suspicious_iam.json`.]

**Say:**
> "We upload a CloudTrail JSON file with two suspicious events: a root console login without MFA, and an IAM privilege escalation."

[ACTION: Show the upload response. Point out `evidence_id` and `input_hash`.]

**Say:**
> "The backend immediately returns a SHA-256 hash of the raw bytes. That hash is the fingerprint we will verify against later."

---

### Step 2 — Run analysis (1:10 – 1:30)

[ACTION: Click Run Analysis.]

**Say:**
> "Five agents run in sequence. The policy engine evaluates the events first. It finds two matches: root login without MFA — Critical — and IAM privilege escalation — High."

[ACTION: Show the findings panel. Point out `rule_id`, `severity`, and `recommended_action`.]

**Say:**
> "Severity comes from the policy rules, not from the LLM. The AI is only allowed to enrich report prose — it cannot change the risk level or compliance status."

---

### Step 3 — Verification record (1:30 – 1:50)

[ACTION: Navigate to the Auditor Verification view. Show the committed record.]

**Say:**
> "The verification record contains three hashes: input hash — a fingerprint of the uploaded file. Policy hash — a fingerprint of the exact policy version used. Result hash — a fingerprint of the full analysis output. No raw logs, no asset names, no usernames. Just hashes and a compliance status."

[ACTION: Click Verify. Show `verification_status: VERIFIED` and all three `_match: true`.]

**Say:**
> "All three match. Verification passes."

---

### Step 4 — Tamper detection (1:50 – 2:15)

[ACTION: Navigate to the Tamper Detection view. Click Tamper: Input.]

**Say:**
> "Now we simulate an attacker modifying the evidence after analysis. The demo endpoint replaces the stored bytes without touching the committed hashes."

[ACTION: Show the verification result: `verification_status: FAILED`, `input_hash_match: false`, `mismatch_reason: Input hash mismatch`.]

**Say:**
> "The hash no longer matches. Verification fails immediately, and the auditor sees exactly which component was tampered with. We can demonstrate the same for policy tampering and result tampering."

---

## What the AI Agent Does (2:15 – 2:25)

**Say:**
> "Five agents run in a fixed pipeline: Ingestion normalizes the file, Risk Analysis applies policy rules, Compliance sets pass or fail, Report Agent writes the markdown report, and Verification Agent computes and commits the three hashes. The LLM only runs at the report step, and only if an OpenAI key is configured. If it is not, the deterministic report is used as-is."

---

## What the Midnight Record Proves (2:25 – 2:35)

**Say:**
> "The three hashes together prove: this specific evidence file was analyzed under this specific policy version and produced this specific result. If any one of those three things changes, verification fails. The committed record is currently written to a mock Midnight adapter — it simulates a blockchain commit and returns a transaction ID, but it is in-memory. A real Midnight integration would make the record immutable on-chain."

---

## Current Limitations (2:35 – 2:45)

**Say:**
> "Three honest limitations. First: all state is in-memory — a backend restart clears everything. Second: the Midnight adapter is mocked — the transaction ID is simulated, not on-chain. Third: authentication is optional in local development — the API key check is bypassed when `API_KEY` is not set in the environment."

---

## Post-Hackathon Roadmap (2:45 – 3:00)

**Say:**
> "Post-hackathon priorities in order: replace in-memory stores with PostgreSQL and private object storage, replace the mock Midnight adapter with a real Midnight integration, add immutable policy version records, then add role-based access control and direct integrations for CloudTrail and SIEM tools. The core verification model is already complete — the remaining work is production hardening."

---

## Reference — What Each Hash Covers

| Hash | Source | Changes when... |
|---|---|---|
| `input_hash` | SHA-256 of uploaded file bytes | Evidence file is modified |
| `policy_hash` | SHA-256 of policy rule definitions | Policy version is updated |
| `result_hash` | SHA-256 of full analysis output (findings, risk level, compliance status, report, analysis ID) | Any analysis output changes |

## Reference — Verified Sample Values

Running the demo against `samples/cloudtrail_suspicious_iam.json` always produces:

```
input_hash  : 825cbc2a7ba5bb28adfa5bf8c5b3d0b4ac491431e0965faf48f1036cf41f3f5e
policy_hash : fe5d6f82addb81acf77912b2e65e4367d3a36c1713561983131a531bdde76bf8
risk_level  : CRITICAL
compliance  : FAILED
findings    : 2 (Root MFA — Critical, IAM escalation — High)
```

`result_hash` varies per run because it covers the analysis ID, which is a new UUID each time.

## Reference — Backend Endpoints Used in Demo

| Step | Method | Path |
|---|---|---|
| Health | GET | `/health` |
| Upload | POST | `/api/evidence/upload` |
| Analyze | POST | `/api/analysis/run/{evidence_id}` |
| View record | GET | `/api/verification/{analysis_id}` |
| Verify | POST | `/api/verification/{analysis_id}/verify` |
| Tamper input | POST | `/api/demo/tamper/{analysis_id}/input` |
| Tamper policy | POST | `/api/demo/tamper/{analysis_id}/policy` |
| Tamper result | POST | `/api/demo/tamper/{analysis_id}/result` |

*Tamper endpoints require `DEMO_MODE=true` in the backend environment.*
