from fastapi import APIRouter, HTTPException

from app.schemas.analysis import AnalysisPlaceholderResponse, AnalysisRunResponse
from app.services.analysis_service import AnalysisService, EvidenceNotFoundError

router = APIRouter()
analysis_service = AnalysisService()


@router.get("/{analysis_id}", response_model=AnalysisPlaceholderResponse)
def get_analysis_placeholder(analysis_id: str) -> AnalysisPlaceholderResponse:
    return AnalysisPlaceholderResponse(
        analysis_id=analysis_id,
        status="not_implemented",
        message="Analysis retrieval will be implemented in a later milestone.",
    )


@router.post("/run/{evidence_id}", response_model=AnalysisRunResponse)
def run_analysis(evidence_id: str) -> AnalysisRunResponse:
    try:
        return analysis_service.run(evidence_id)
    except EvidenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Evidence not found.") from exc
