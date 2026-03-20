from fastapi import APIRouter

from app.application.schemas.common import MessageResponse
from app.application.schemas.platform import AppSettingUpsertRequest, AppSettingsResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=AppSettingsResponse)
def list_settings(services: ServiceBundleDep) -> AppSettingsResponse:
    return services.settings.list()


@router.put("", response_model=MessageResponse)
def upsert_setting(payload: AppSettingUpsertRequest, services: ServiceBundleDep) -> MessageResponse:
    services.settings.upsert(payload)
    return MessageResponse(message="설정이 저장되었습니다.")
