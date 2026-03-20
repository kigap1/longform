from fastapi import APIRouter

from app.application.schemas.platform import ProjectCreateRequest, ProjectListResponse, ProjectSummary
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=ProjectListResponse)
def list_projects(services: ServiceBundleDep) -> ProjectListResponse:
    return services.projects.list()


@router.post("", response_model=ProjectSummary)
def create_project(payload: ProjectCreateRequest, services: ServiceBundleDep) -> ProjectSummary:
    return services.projects.create(payload)
