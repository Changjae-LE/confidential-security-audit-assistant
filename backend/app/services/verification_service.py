from app.schemas.verification import VerificationResult
from app.schemas.verification_record import VerificationRecord
from app.services.analysis_service import get_analysis_snapshot
from app.services.evidence_service import get_evidence_content
from app.services.hash_service import sha256_hex, sha256_json
from app.services.midnight_adapter import get_mock_midnight_record


class VerificationNotFoundError(Exception):
    pass


def get_verification_record(analysis_id: str) -> VerificationRecord:
    record = get_mock_midnight_record(analysis_id)
    if record is None:
        raise VerificationNotFoundError(analysis_id)
    return record


def verify_analysis(analysis_id: str) -> VerificationResult:
    record = get_verification_record(analysis_id)
    snapshot = get_analysis_snapshot(analysis_id)
    if snapshot is None:
        raise VerificationNotFoundError(analysis_id)

    evidence_content = get_evidence_content(snapshot["evidence_id"])
    if evidence_content is None:
        raise VerificationNotFoundError(analysis_id)

    current_input_hash = sha256_hex(evidence_content)
    current_policy_hash = sha256_json(snapshot["policy_payload"])
    current_result_hash = sha256_json(snapshot["result_payload"])

    input_hash_match = current_input_hash == record.input_hash
    policy_hash_match = current_policy_hash == record.policy_hash
    result_hash_match = current_result_hash == record.result_hash
    mismatch_reason = _mismatch_reason(input_hash_match, policy_hash_match, result_hash_match)

    return VerificationResult(
        analysis_id=analysis_id,
        verification_status="FAILED" if mismatch_reason else "VERIFIED",
        mismatch_reason=mismatch_reason,
        input_hash_match=input_hash_match,
        policy_hash_match=policy_hash_match,
        result_hash_match=result_hash_match,
        record=record,
    )


def _mismatch_reason(
    input_hash_match: bool,
    policy_hash_match: bool,
    result_hash_match: bool,
) -> str | None:
    if not input_hash_match:
        return "Input hash mismatch"
    if not policy_hash_match:
        return "Policy hash mismatch"
    if not result_hash_match:
        return "Result hash mismatch"
    return None
