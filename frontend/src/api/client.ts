import type {
  AnalysisRunResponse,
  EvidenceUploadResponse,
  TamperType,
  VerificationRecord,
  VerificationResult,
} from "../types/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function uploadEvidence(file: File): Promise<EvidenceUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<EvidenceUploadResponse>("/api/evidence/upload", {
    method: "POST",
    body: formData,
  });
}

export async function runAnalysis(evidenceId: string): Promise<AnalysisRunResponse> {
  return request<AnalysisRunResponse>(`/api/analysis/run/${evidenceId}`, {
    method: "POST",
  });
}

export async function getVerification(analysisId: string): Promise<VerificationRecord> {
  return request<VerificationRecord>(`/api/verification/${analysisId}`);
}

export async function verifyAnalysis(analysisId: string): Promise<VerificationResult> {
  return request<VerificationResult>(`/api/verification/${analysisId}/verify`, {
    method: "POST",
  });
}

export async function tamperAnalysis(
  analysisId: string,
  tamperType: TamperType,
): Promise<VerificationResult> {
  return request<VerificationResult>(`/api/demo/tamper/${analysisId}/${tamperType}`, {
    method: "POST",
  });
}
