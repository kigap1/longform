from fastapi import APIRouter

from app.application.schemas.common import MessageResponse
from app.application.schemas.platform import AIProviderCatalogResponse, AppSettingUpsertRequest, AppSettingsResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=AppSettingsResponse)
def list_settings(services: ServiceBundleDep) -> AppSettingsResponse:
    return services.settings.list()


@router.get("/ai-providers", response_model=AIProviderCatalogResponse)
def list_ai_providers(services: ServiceBundleDep) -> AIProviderCatalogResponse:
    return services.settings.ai_provider_catalog()


@router.put("", response_model=MessageResponse)
def upsert_setting(payload: AppSettingUpsertRequest, services: ServiceBundleDep) -> MessageResponse:
    services.settings.upsert(payload)
    return MessageResponse(message="설정이 저장되었습니다.")
