from fastapi import APIRouter, Depends

from app.api import analysis, demo, evidence, health, verification
from app.api.dependencies import verify_api_key

_auth = [Depends(verify_api_key)]

api_router = APIRouter()
api_router.include_router(health.router)  # health stays open — no auth required
api_router.include_router(evidence.router, prefix="/api/evidence", tags=["evidence"], dependencies=_auth)
api_router.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"], dependencies=_auth)
api_router.include_router(
    verification.router,
    prefix="/api/verification",
    tags=["verification"],
    dependencies=_auth,
)
api_router.include_router(demo.router, prefix="/api/demo", tags=["demo"], dependencies=_auth)
