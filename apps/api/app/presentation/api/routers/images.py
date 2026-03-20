from fastapi import APIRouter

from app.application.schemas.assets import (
    ImageAssetSummary,
    ImageGenerateRequest,
    ImageRegenerateSceneRequest,
    SceneImagePromptSummary,
    SceneImagePromptUpdateRequest,
)
from app.presentation.api.errors import raise_service_http_error
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/generate", response_model=ImageAssetSummary)
def generate_image(payload: ImageGenerateRequest, services: ServiceBundleDep) -> ImageAssetSummary:
    try:
        return services.images.generate(payload)
    except Exception as exc:
        raise_service_http_error(exc)


@router.post("/regenerate-scene", response_model=ImageAssetSummary)
def regenerate_scene_image(payload: ImageRegenerateSceneRequest, services: ServiceBundleDep) -> ImageAssetSummary:
    try:
        return services.images.regenerate_scene(payload)
    except Exception as exc:
        raise_service_http_error(exc)


@router.patch("/scene-prompt", response_model=SceneImagePromptSummary)
def update_scene_prompt(payload: SceneImagePromptUpdateRequest, services: ServiceBundleDep) -> SceneImagePromptSummary:
    try:
        return services.images.update_scene_prompt(payload)
    except Exception as exc:
        raise_service_http_error(exc)
