from __future__ import annotations

from pydantic import Field

from app.application.schemas.common import APIModel


class InfographicStatCalloutInput(APIModel):
    label: str
    value: str
    emphasis: str = "medium"


class KoreanInfographicLayoutInput(APIModel):
    aspect_ratio: str = "9:16"
    layout_style: str = "앵커+차트"
    headline: str = ""
    subheadline: str = ""
    stat_callouts: list[InfographicStatCalloutInput] = Field(default_factory=list)
    caption_lines: list[str] = Field(default_factory=list)
    color_tokens: list[str] = Field(default_factory=lambda: ["navy", "crimson", "ivory"])


class CharacterProfileSummary(APIModel):
    id: str
    name: str
    description: str
    style_rules: list[str] = Field(default_factory=list)
    prompt_template: str
    reference_assets: list[str] = Field(default_factory=list)
    locked: bool = False


class CharacterListResponse(APIModel):
    project_id: str | None = None
    locked_character_profile_id: str | None = None
    items: list[CharacterProfileSummary]


class ImageGenerateRequest(APIModel):
    project_id: str
    scene_id: str
    character_profile_id: str | None = None
    prompt: str = ""
    prompt_override: str | None = None
    reference_snapshot_ids: list[str] = Field(default_factory=list)
    layout: KoreanInfographicLayoutInput | None = None
    user_instructions: str = ""


class ImageRegenerateSceneRequest(APIModel):
    project_id: str
    scene_id: str
    character_profile_id: str | None = None
    prompt_override: str | None = None
    reference_snapshot_ids: list[str] = Field(default_factory=list)
    layout: KoreanInfographicLayoutInput | None = None
    user_instructions: str = ""


class SceneImagePromptUpdateRequest(APIModel):
    project_id: str
    scene_id: str
    prompt: str


class SceneImagePromptSummary(APIModel):
    scene_id: str
    scene_title: str
    image_prompt: str


class ImageAssetSummary(APIModel):
    id: str
    scene_id: str
    scene_title: str
    prompt: str
    asset_url: str
    thumbnail_url: str
    status: str
    provider_name: str = ""
    character_profile_id: str | None = None
    character_name: str = ""
    project_locked_character: bool = False
    reference_snapshot_ids: list[str] = Field(default_factory=list)
    layout: KoreanInfographicLayoutInput | None = None
    revision_note: str = ""


class VerticalVideoInstructionsInput(APIModel):
    aspect_ratio: str = "9:16"
    duration_seconds: int = 8
    framing: str = "세로형 프레임, 인물 중심, 자막 안전영역 확보"
    caption_style: str = "굵은 한국어 자막"
    pacing: str = "steady"
    motion_emphasis: str = "medium"


class VideoPrepareRequest(APIModel):
    project_id: str
    scene_ids: list[str]
    vertical_instructions: VerticalVideoInstructionsInput = Field(default_factory=VerticalVideoInstructionsInput)
    include_latest_image: bool = True
    user_instructions: str = ""


class VideoExecutionRequest(APIModel):
    project_id: str
    video_asset_ids: list[str]
    user_instructions: str = ""


class VideoAssetSummary(APIModel):
    id: str
    scene_id: str
    scene_title: str = ""
    image_asset_id: str | None = None
    prompt: str
    motion_notes: str
    bundle_path: str
    bundle_download_path: str = ""
    status: str
    provider_name: str = ""
    provider_mode: str = ""
    vertical_instructions: VerticalVideoInstructionsInput | None = None
    job_id: str = ""


class VideoExecutionSummary(APIModel):
    video_asset_id: str
    scene_id: str
    status: str
    provider_name: str = ""
    provider_mode: str = ""
    provider_job_id: str = ""
    output_path: str
    bundle_path: str
    job_id: str = ""
