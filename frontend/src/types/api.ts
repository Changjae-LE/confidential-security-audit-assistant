export type EvidenceUploadResponse = {
  evidence_id: string;
  filename: string;
  content_type: string;
  input_hash: string;
  uploaded_at: string;
};

export type Finding = {
  title: string;
  severity: string;
  evidence_summary: string;
  affected_asset: string;
  rule_id: string;
  recommended_action: string;
  confidence_score: number;
};

export type VerificationRecord = {
  analysis_id: string;
  input_hash: string;
  policy_hash: string;
  result_hash: string;
  risk_level: string;
  compliance_status: string;
  verification_status: string;
  committed_at: string | null;
  mock_tx_id: string;
};

export type AnalysisRunResponse = {
  analysis_id: string;
  findings: Finding[];
  risk_level: string;
  compliance_status: string;
  report: string;
  verification_record: VerificationRecord;
};

export type VerificationResult = {
  analysis_id: string;
  verification_status: string;
  mismatch_reason: string | null;
  input_hash_match: boolean;
  policy_hash_match: boolean;
  result_hash_match: boolean;
  record: VerificationRecord;
};

export type TamperType = "input" | "policy" | "result";
