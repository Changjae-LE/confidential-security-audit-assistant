import {
  AlertTriangle,
  CheckCircle2,
  FileSearch,
  FileText,
  LockKeyhole,
  RefreshCw,
  ShieldCheck,
  Upload,
} from "lucide-react";
import { useState } from "react";

import {
  getVerification,
  runAnalysis,
  tamperAnalysis,
  uploadEvidence,
  verifyAnalysis,
} from "./api/client";
import type {
  AnalysisRunResponse,
  EvidenceUploadResponse,
  TamperType,
  VerificationRecord,
  VerificationResult,
} from "./types/api";

type Page = "upload" | "analysis" | "auditor" | "tamper";

const pages: Array<{ id: Page; label: string; icon: typeof Upload }> = [
  { id: "upload", label: "Upload Evidence", icon: Upload },
  { id: "analysis", label: "Analysis Results", icon: FileSearch },
  { id: "auditor", label: "Auditor Verification", icon: ShieldCheck },
  { id: "tamper", label: "Tamper Detection", icon: AlertTriangle },
];

function App() {
  const [page, setPage] = useState<Page>("upload");
  const [evidence, setEvidence] = useState<EvidenceUploadResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisRunResponse | null>(null);
  const [verification, setVerification] = useState<VerificationRecord | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleUpload(file: File) {
    setBusy(true);
    setError(null);
    try {
      const uploaded = await uploadEvidence(file);
      setEvidence(uploaded);
      setAnalysis(null);
      setVerification(null);
      setVerificationResult(null);
      setPage("analysis");
    } catch (uploadError) {
      setError(errorMessage(uploadError));
    } finally {
      setBusy(false);
    }
  }

  async function handleRunAnalysis() {
    if (!evidence) return;
    setBusy(true);
    setError(null);
    try {
      const result = await runAnalysis(evidence.evidence_id);
      setAnalysis(result);
      setVerification(result.verification_record);
      setVerificationResult(null);
      setPage("analysis");
    } catch (analysisError) {
      setError(errorMessage(analysisError));
    } finally {
      setBusy(false);
    }
  }

  async function handleLoadVerification() {
    if (!analysis) return;
    setBusy(true);
    setError(null);
    try {
      setVerification(await getVerification(analysis.analysis_id));
      setPage("auditor");
    } catch (verificationError) {
      setError(errorMessage(verificationError));
    } finally {
      setBusy(false);
    }
  }

  async function handleVerify() {
    if (!analysis) return;
    setBusy(true);
    setError(null);
    try {
      setVerificationResult(await verifyAnalysis(analysis.analysis_id));
    } catch (verificationError) {
      setError(errorMessage(verificationError));
    } finally {
      setBusy(false);
    }
  }

  async function handleTamper(tamperType: TamperType) {
    if (!analysis) return;
    setBusy(true);
    setError(null);
    try {
      setVerificationResult(await tamperAnalysis(analysis.analysis_id, tamperType));
      setPage("tamper");
    } catch (tamperError) {
      setError(errorMessage(tamperError));
    } finally {
      setBusy(false);
    }
  }

  let activeContent;
  if (page === "upload") {
    activeContent = <UploadPage busy={busy} evidence={evidence} onUpload={handleUpload} />;
  } else if (page === "analysis") {
    activeContent = (
      <AnalysisPage
        analysis={analysis}
        busy={busy}
        evidence={evidence}
        onRunAnalysis={handleRunAnalysis}
      />
    );
  } else if (page === "auditor") {
    activeContent = (
      <AuditorPage
        analysis={analysis}
        busy={busy}
        verification={verification}
        verificationResult={verificationResult}
        onLoadVerification={handleLoadVerification}
        onVerify={handleVerify}
      />
    );
  } else {
    activeContent = (
      <TamperPage
        analysis={analysis}
        busy={busy}
        verificationResult={verificationResult}
        onTamper={handleTamper}
      />
    );
  }

  return (
    <main className="min-h-screen bg-panel text-ink">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-normal">
                Confidential Security Audit Assistant
              </h1>
              <p className="mt-1 max-w-3xl text-sm text-slate-600">
                Private evidence analysis with deterministic findings and tamper-evident verification.
              </p>
            </div>
            <StatusStrip evidence={evidence} analysis={analysis} />
          </div>
          <nav className="grid grid-cols-2 gap-2 lg:grid-cols-4">
            {pages.map((item) => {
              const Icon = item.icon;
              const isActive = page === item.id;
              return (
                <button
                  key={item.id}
                  className={`flex h-11 items-center justify-center gap-2 rounded-md border px-3 text-sm font-medium transition ${
                    isActive
                      ? "border-ink bg-ink text-white"
                      : "border-line bg-white text-slate-700 hover:border-slate-400"
                  }`}
                  type="button"
                  onClick={() => setPage(item.id)}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {error ? (
          <div className="mb-4 flex items-start gap-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-danger">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : null}
        {activeContent}
      </div>
    </main>
  );
}

type UploadPageProps = {
  busy: boolean;
  evidence: EvidenceUploadResponse | null;
  onUpload: (file: File) => void;
};

function UploadPage({ busy, evidence, onUpload }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);

  return (
    <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_420px]">
      <div className="rounded-md border border-line bg-white p-5">
        <div className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-mint" />
          <h2 className="text-lg font-semibold">Upload Evidence</h2>
        </div>
        <div className="mt-5 flex flex-col gap-4">
          <input
            className="block w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
            type="file"
            accept=".json,.csv,application/json,text/csv"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button
            className="inline-flex h-10 w-fit items-center gap-2 rounded-md bg-ink px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
            disabled={!file || busy}
            type="button"
            onClick={() => file && onUpload(file)}
          >
            <Upload className="h-4 w-4" />
            Upload
          </button>
        </div>
      </div>
      <EvidencePanel evidence={evidence} />
    </section>
  );
}

type AnalysisPageProps = {
  analysis: AnalysisRunResponse | null;
  busy: boolean;
  evidence: EvidenceUploadResponse | null;
  onRunAnalysis: () => void;
};

function AnalysisPage({ analysis, busy, evidence, onRunAnalysis }: AnalysisPageProps) {
  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 rounded-md border border-line bg-white p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Analysis Results</h2>
          <p className="mt-1 text-sm text-slate-600">{evidence?.filename ?? "No evidence uploaded"}</p>
        </div>
        <button
          className="inline-flex h-10 w-fit items-center gap-2 rounded-md bg-ink px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={!evidence || busy}
          type="button"
          onClick={onRunAnalysis}
        >
          <FileSearch className="h-4 w-4" />
          Run Analysis
        </button>
      </div>

      {analysis ? (
        <>
          <div className="grid gap-3 md:grid-cols-3">
            <Metric label="Analysis ID" value={analysis.analysis_id} />
            <Metric label="Risk Level" value={analysis.risk_level} tone={riskTone(analysis.risk_level)} />
            <Metric label="Compliance" value={analysis.compliance_status} tone="amber" />
          </div>
          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_420px]">
            <FindingsList analysis={analysis} />
            <ReportPanel report={analysis.report} />
          </div>
        </>
      ) : (
        <EmptyState icon={FileSearch} title="Analysis waiting" />
      )}
    </section>
  );
}

type AuditorPageProps = {
  analysis: AnalysisRunResponse | null;
  busy: boolean;
  verification: VerificationRecord | null;
  verificationResult: VerificationResult | null;
  onLoadVerification: () => void;
  onVerify: () => void;
};

function AuditorPage({
  analysis,
  busy,
  verification,
  verificationResult,
  onLoadVerification,
  onVerify,
}: AuditorPageProps) {
  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 rounded-md border border-line bg-white p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Auditor Verification</h2>
          <p className="mt-1 text-sm text-slate-600">{analysis?.analysis_id ?? "No committed analysis"}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-4 text-sm font-medium disabled:cursor-not-allowed disabled:text-slate-400"
            disabled={!analysis || busy}
            type="button"
            onClick={onLoadVerification}
          >
            <LockKeyhole className="h-4 w-4" />
            Load Record
          </button>
          <button
            className="inline-flex h-10 items-center gap-2 rounded-md bg-ink px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
            disabled={!analysis || busy}
            type="button"
            onClick={onVerify}
          >
            <ShieldCheck className="h-4 w-4" />
            Verify
          </button>
        </div>
      </div>
      {verification ? <VerificationPanel record={verification} result={verificationResult} /> : null}
      {!verification ? <EmptyState icon={ShieldCheck} title="Verification record waiting" /> : null}
    </section>
  );
}

type TamperPageProps = {
  analysis: AnalysisRunResponse | null;
  busy: boolean;
  verificationResult: VerificationResult | null;
  onTamper: (tamperType: TamperType) => void;
};

function TamperPage({ analysis, busy, verificationResult, onTamper }: TamperPageProps) {
  const actions: Array<{ id: TamperType; label: string }> = [
    { id: "input", label: "Input Hash" },
    { id: "policy", label: "Policy Hash" },
    { id: "result", label: "Result Hash" },
  ];

  return (
    <section className="space-y-4">
      <div className="rounded-md border border-line bg-white p-5">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber" />
          <h2 className="text-lg font-semibold">Tamper Detection Demo</h2>
        </div>
        <div className="mt-5 grid gap-2 sm:grid-cols-3">
          {actions.map((action) => (
            <button
              key={action.id}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={!analysis || busy}
              type="button"
              onClick={() => onTamper(action.id)}
            >
              <RefreshCw className="h-4 w-4" />
              {action.label}
            </button>
          ))}
        </div>
      </div>
      {verificationResult ? (
        <VerificationResultPanel result={verificationResult} />
      ) : (
        <EmptyState icon={AlertTriangle} title="Tamper result waiting" />
      )}
    </section>
  );
}

function StatusStrip({
  evidence,
  analysis,
}: {
  evidence: EvidenceUploadResponse | null;
  analysis: AnalysisRunResponse | null;
}) {
  return (
    <div className="grid grid-cols-2 gap-2 text-xs md:w-[360px]">
      <StatusPill label="Evidence" ready={Boolean(evidence)} />
      <StatusPill label="Analysis" ready={Boolean(analysis)} />
    </div>
  );
}

function StatusPill({ label, ready }: { label: string; ready: boolean }) {
  return (
    <div className="flex h-9 items-center justify-between rounded-md border border-line bg-panel px-3">
      <span className="font-medium">{label}</span>
      {ready ? <CheckCircle2 className="h-4 w-4 text-mint" /> : <span className="h-2 w-2 rounded-full bg-slate-300" />}
    </div>
  );
}

function EvidencePanel({ evidence }: { evidence: EvidenceUploadResponse | null }) {
  return (
    <aside className="rounded-md border border-line bg-white p-5">
      <h2 className="text-lg font-semibold">Evidence Metadata</h2>
      {evidence ? (
        <dl className="mt-4 space-y-3 text-sm">
          <KeyValue label="Evidence ID" value={evidence.evidence_id} />
          <KeyValue label="Filename" value={evidence.filename} />
          <KeyValue label="Content Type" value={evidence.content_type} />
          <KeyValue label="Input Hash" value={evidence.input_hash} mono />
          <KeyValue label="Uploaded At" value={formatDate(evidence.uploaded_at)} />
        </dl>
      ) : (
        <EmptyState icon={FileText} title="No evidence metadata" compact />
      )}
    </aside>
  );
}

function FindingsList({ analysis }: { analysis: AnalysisRunResponse }) {
  return (
    <div className="rounded-md border border-line bg-white p-5">
      <h2 className="text-lg font-semibold">Findings</h2>
      <div className="mt-4 space-y-3">
        {analysis.findings.map((finding) => (
          <article key={finding.rule_id} className="rounded-md border border-line p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h3 className="font-semibold">{finding.title}</h3>
              <Badge tone={riskTone(finding.severity)}>{finding.severity}</Badge>
            </div>
            <dl className="mt-3 grid gap-2 text-sm md:grid-cols-2">
              <KeyValue label="Rule" value={finding.rule_id} />
              <KeyValue label="Affected Asset" value={finding.affected_asset} />
              <KeyValue label="Evidence Summary" value={finding.evidence_summary} />
              <KeyValue label="Recommended Action" value={finding.recommended_action} />
              <KeyValue label="Confidence" value={finding.confidence_score.toFixed(2)} />
            </dl>
          </article>
        ))}
      </div>
    </div>
  );
}

function ReportPanel({ report }: { report: string }) {
  return (
    <aside className="rounded-md border border-line bg-white p-5">
      <h2 className="text-lg font-semibold">Report</h2>
      <pre className="mt-4 max-h-[560px] overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs leading-5 text-slate-100">
        {report}
      </pre>
    </aside>
  );
}

function VerificationPanel({
  record,
  result,
}: {
  record: VerificationRecord;
  result: VerificationResult | null;
}) {
  const currentStatus = result?.verification_status ?? record.verification_status;
  const failed = currentStatus === "FAILED";
  const verified = currentStatus === "VERIFIED" || currentStatus === "COMMITTED";

  return (
    <div className="space-y-4">
      <div
        className={`flex items-center gap-3 rounded-md border p-4 ${
          failed
            ? "border-red-200 bg-red-50 text-danger"
            : verified
              ? "border-emerald-200 bg-emerald-50 text-mint"
              : "border-line bg-white text-ink"
        }`}
      >
        {failed ? <AlertTriangle className="h-5 w-5" /> : <ShieldCheck className="h-5 w-5" />}
        <div>
          <p className="font-semibold">
            {failed ? "Verification failed" : "Verification record is valid"}
          </p>
          <p className="text-sm">
            {result?.mismatch_reason ?? "Stored hashes are available for auditor verification."}
          </p>
        </div>
      </div>
      <div className="rounded-md border border-line bg-white p-5">
        <h2 className="text-lg font-semibold">Committed Record</h2>
        <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
          <KeyValue label="Analysis ID" value={record.analysis_id} />
          <KeyValue label="Timestamp" value={record.committed_at ? formatDate(record.committed_at) : "Pending"} />
          <KeyValue label="Input Hash" value={record.input_hash} mono />
          <KeyValue label="Policy Hash" value={record.policy_hash} mono />
          <KeyValue label="Result Hash" value={record.result_hash} mono />
          <KeyValue label="Risk Level" value={record.risk_level} />
          <KeyValue label="Compliance" value={record.compliance_status} />
          <KeyValue label="Verification Status" value={currentStatus} />
          <KeyValue label="Mock TX ID" value={record.mock_tx_id} />
          {result?.mismatch_reason ? (
            <KeyValue label="Mismatch Reason" value={result.mismatch_reason} />
          ) : null}
        </dl>
      </div>
      {result ? <VerificationResultPanel result={result} /> : null}
    </div>
  );
}

function VerificationResultPanel({ result }: { result: VerificationResult }) {
  const failed = result.verification_status === "FAILED";
  return (
    <aside
      className={`rounded-md border p-5 ${
        failed
          ? "border-red-300 bg-red-50 ring-2 ring-red-100"
          : "border-emerald-300 bg-emerald-50 ring-2 ring-emerald-100"
      }`}
    >
      <div className="flex items-center gap-2">
        {failed ? <AlertTriangle className="h-5 w-5 text-danger" /> : <ShieldCheck className="h-5 w-5 text-mint" />}
        <h2 className={`text-lg font-semibold ${failed ? "text-danger" : "text-mint"}`}>
          {failed ? "Tamper Detected" : "Verification Successful"}
        </h2>
      </div>
      <dl className="mt-4 space-y-3 text-sm">
        <KeyValue label="Verification Status" value={result.verification_status} />
        <KeyValue label="Mismatch Reason" value={result.mismatch_reason ?? "All hashes match"} />
        <KeyValue label="Input Hash Match" value={String(result.input_hash_match)} />
        <KeyValue label="Policy Hash Match" value={String(result.policy_hash_match)} />
        <KeyValue label="Result Hash Match" value={String(result.result_hash_match)} />
      </dl>
    </aside>
  );
}

function Metric({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "red" | "amber" | "green";
}) {
  return (
    <div className="rounded-md border border-line bg-white p-4">
      <p className="text-xs font-medium uppercase text-slate-500">{label}</p>
      <p className={`mt-2 break-words text-lg font-semibold ${toneClass(tone)}`}>{value}</p>
    </div>
  );
}

function KeyValue({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase text-slate-500">{label}</dt>
      <dd className={`mt-1 break-words text-slate-800 ${mono ? "font-mono text-xs" : ""}`}>{value}</dd>
    </div>
  );
}

function Badge({ children, tone }: { children: string; tone: "default" | "red" | "amber" | "green" }) {
  return (
    <span className={`inline-flex h-7 items-center rounded-md px-2 text-xs font-semibold ${badgeClass(tone)}`}>
      {children}
    </span>
  );
}

function EmptyState({
  icon: Icon,
  title,
  compact = false,
}: {
  icon: typeof FileSearch;
  title: string;
  compact?: boolean;
}) {
  return (
    <div
      className={`flex items-center justify-center rounded-md border border-dashed border-line bg-white text-slate-500 ${
        compact ? "mt-4 h-32" : "h-56"
      }`}
    >
      <div className="text-center">
        <Icon className="mx-auto h-7 w-7" />
        <p className="mt-2 text-sm font-medium">{title}</p>
      </div>
    </div>
  );
}

function riskTone(value: string): "default" | "red" | "amber" | "green" {
  const normalized = value.toLowerCase();
  if (normalized === "critical" || normalized === "high") return "red";
  if (normalized === "medium" || normalized === "failed") return "amber";
  if (normalized === "low" || normalized === "pass" || normalized === "verified") return "green";
  return "default";
}

function toneClass(tone: "default" | "red" | "amber" | "green") {
  return {
    default: "text-ink",
    red: "text-danger",
    amber: "text-amber",
    green: "text-mint",
  }[tone];
}

function badgeClass(tone: "default" | "red" | "amber" | "green") {
  return {
    default: "bg-slate-100 text-slate-700",
    red: "bg-red-100 text-danger",
    amber: "bg-amber-100 text-amber",
    green: "bg-emerald-100 text-mint",
  }[tone];
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Unexpected error";
}

export default App;
