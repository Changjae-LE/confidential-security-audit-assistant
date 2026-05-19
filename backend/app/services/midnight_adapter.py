from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.verification_record import VerificationRecord

_records: dict[str, VerificationRecord] = {}


class MockMidnightAdapter:
    def commit(self, record: VerificationRecord) -> VerificationRecord:
        committed_record = record.model_copy(
            update={
                "verification_status": "COMMITTED",
                "committed_at": datetime.now(timezone.utc),
                "mock_tx_id": f"MOCK-MIDNIGHT-{uuid4().hex[:12].upper()}",
            }
        )
        _records[committed_record.analysis_id] = committed_record
        return committed_record


def get_mock_midnight_record(analysis_id: str) -> VerificationRecord | None:
    return _records.get(analysis_id)
