from fastapi import APIRouter, Query

from app.application.schemas.scripts import (
    RegenerateSectionRequest,
    RegenerateSectionResponse,
    ScriptGenerationRequest,
    ScriptSummary,
)
from app.presentation.api.errors import raise_service_http_error
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("/latest", response_model=ScriptSummary | None)
def latest_script(services: ServiceBundleDep, project_id: str = Query(...)) -> ScriptSummary | None:
    return services.scripts.latest(project_id)


@router.post("/generate", response_model=ScriptSummary)
def generate_script(payload: ScriptGenerationRequest, services: ServiceBundleDep) -> ScriptSummary:
    try:
        return services.scripts.generate(payload)
    except Exception as exc:
        raise_service_http_error(exc)


@router.post("/regenerate-section", response_model=RegenerateSectionResponse)
def regenerate_section(payload: RegenerateSectionRequest, services: ServiceBundleDep) -> RegenerateSectionResponse:
    try:
        return services.scripts.regenerate_section(payload)
    except Exception as exc:
        raise_service_http_error(exc)
