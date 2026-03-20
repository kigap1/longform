from fastapi import APIRouter, Query

from app.application.schemas.assets import CharacterListResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=CharacterListResponse)
def list_characters(services: ServiceBundleDep, project_id: str | None = Query(None)) -> CharacterListResponse:
    return services.characters.list(project_id)
