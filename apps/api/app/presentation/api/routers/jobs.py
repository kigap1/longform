from fastapi import APIRouter, Query

from app.application.schemas.common import JobSummary
from app.application.schemas.platform import JobDetailResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=list[JobSummary])
def list_jobs(services: ServiceBundleDep, project_id: str | None = Query(None)) -> list[JobSummary]:
    return services.jobs.list(project_id)


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: str, services: ServiceBundleDep) -> JobDetailResponse:
    return services.jobs.detail(job_id)
