from fastapi import APIRouter

from app.application.schemas.assets import (
    ImageAssetSummary,
    ImageGenerateRequest,
    ImageRegenerateSceneRequest,
    SceneImagePromptSummary,
    SceneImagePromptUpdateRequest,
)
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/generate", response_model=ImageAssetSummary)
def generate_image(payload: ImageGenerateRequest, services: ServiceBundleDep) -> ImageAssetSummary:
    return services.images.generate(payload)


@router.post("/regenerate-scene", response_model=ImageAssetSummary)
def regenerate_scene_image(payload: ImageRegenerateSceneRequest, services: ServiceBundleDep) -> ImageAssetSummary:
    return services.images.regenerate_scene(payload)


@router.patch("/scene-prompt", response_model=SceneImagePromptSummary)
def update_scene_prompt(payload: SceneImagePromptUpdateRequest, services: ServiceBundleDep) -> SceneImagePromptSummary:
    return services.images.update_scene_prompt(payload)
