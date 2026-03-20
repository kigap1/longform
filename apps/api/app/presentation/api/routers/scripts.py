from fastapi import APIRouter

from app.application.schemas.scripts import (
    RegenerateSectionRequest,
    RegenerateSectionResponse,
    ScriptGenerationRequest,
    ScriptSummary,
)
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/generate", response_model=ScriptSummary)
def generate_script(payload: ScriptGenerationRequest, services: ServiceBundleDep) -> ScriptSummary:
    return services.scripts.generate(payload)


@router.post("/regenerate-section", response_model=RegenerateSectionResponse)
def regenerate_section(payload: RegenerateSectionRequest, services: ServiceBundleDep) -> RegenerateSectionResponse:
    return services.scripts.regenerate_section(payload)
