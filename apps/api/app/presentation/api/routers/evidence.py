from fastapi import APIRouter

from app.application.schemas.platform import EvidenceReportResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("/report/{project_id}", response_model=EvidenceReportResponse)
def evidence_report(project_id: str, services: ServiceBundleDep) -> EvidenceReportResponse:
    return services.evidence.report(project_id)
