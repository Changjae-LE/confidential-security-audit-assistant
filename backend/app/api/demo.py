import os

from fastapi import APIRouter, HTTPException

from app.schemas.verification import VerificationResult
from app.services.analysis_service import get_analysis_snapshot
from app.services.evidence_service import replace_evidence_content
from app.services.verification_service import VerificationNotFoundError, verify_analysis

router = APIRouter()


def _require_demo_mode() -> None:
    if os.getenv("DEMO_MODE", "false").lower() != "true":
        raise HTTPException(status_code=404, detail="Not Found")


@router.post("/tamper/{analysis_id}/input", response_model=VerificationResult)
def tamper_input(analysis_id: str) -> VerificationResult:
    _require_demo_mode()
    snapshot = get_analysis_snapshot(analysis_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    replace_evidence_content(snapshot["evidence_id"], b'{"Records":[]}')
    return _verify(analysis_id)


@router.post("/tamper/{analysis_id}/policy", response_model=VerificationResult)
def tamper_policy(analysis_id: str) -> VerificationResult:
    _require_demo_mode()
    snapshot = get_analysis_snapshot(analysis_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    snapshot["policy_payload"] = {"version": "policy-v2", "rule_ids": []}
    return _verify(analysis_id)


@router.post("/tamper/{analysis_id}/result", response_model=VerificationResult)
def tamper_result(analysis_id: str) -> VerificationResult:
    _require_demo_mode()
    snapshot = get_analysis_snapshot(analysis_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    snapshot["result_payload"] = {"tampered": True}
    return _verify(analysis_id)


def _verify(analysis_id: str) -> VerificationResult:
    try:
        return verify_analysis(analysis_id)
    except VerificationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Verification record not found.") from exc
