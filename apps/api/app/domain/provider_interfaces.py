from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from app.domain.enums import IssueCategory


@dataclass(slots=True)
class NewsArticlePayload:
    title: str
    source_name: str
    published_at: datetime
    url: str
    summary: str
    category: IssueCategory
    credibility_score: float


@dataclass(slots=True)
class TimeSeriesPointPayload:
    date: str
    value: float


@dataclass(slots=True)
class IndicatorPayload:
    code: str
    name: str
    source_name: str
    source_url: str
    description: str
    latest_value: float
    previous_value: float | None
    release_date: str
    frequency: str
    unit: str
    tags: list[str] = field(default_factory=list)
    recommended_reason: str | None = None
    series_points: list[TimeSeriesPointPayload] = field(default_factory=list)


@dataclass(slots=True)
class MarketQuotePayload:
    symbol: str
    display_name: str
    asset_class: str
    source_name: str
    source_url: str
    latest_value: float
    change_percent: float
    as_of: str
    currency: str
    note: str = ""
    tags: list[str] = field(default_factory=list)
    chart_points: list[TimeSeriesPointPayload] = field(default_factory=list)


@dataclass(slots=True)
class SnapshotPayload:
    title: str
    source_title: str
    source_url: str
    captured_at: str
    note: str
    image_url: str
    image_bytes: bytes | None = None
    content_type: str = "image/svg+xml"
    capture_mode: str = "stub"
    integration_boundary_note: str = ""


@dataclass(slots=True)
class ScriptEvidencePayload:
    evidence_id: str
    label: str
    source_kind: str
    source_name: str
    source_url: str
    release_date: str | None = None
    value: float | None = None
    note: str = ""


@dataclass(slots=True)
class ScriptSectionPayload:
    heading: str
    content: str
    evidence_ids: list[str] = field(default_factory=list)
    narration_purpose: str = ""


@dataclass(slots=True)
class ScriptScenePayload:
    title: str
    description: str
    image_prompt: str
    motion_prompt: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScriptEvidenceMappingPayload:
    section_heading: str
    evidence_ids: list[str] = field(default_factory=list)
    rationale: str = ""


@dataclass(slots=True)
class CharacterProfilePayload:
    character_profile_id: str
    name: str
    description: str
    prompt_template: str
    style_rules: list[str] = field(default_factory=list)
    reference_assets: list[str] = field(default_factory=list)
    locked: bool = False


@dataclass(slots=True)
class InfographicStatCalloutPayload:
    label: str
    value: str
    emphasis: str = "medium"


@dataclass(slots=True)
class KoreanInfographicLayoutPayload:
    aspect_ratio: str = "9:16"
    layout_style: str = "앵커+차트"
    headline: str = ""
    subheadline: str = ""
    stat_callouts: list[InfographicStatCalloutPayload] = field(default_factory=list)
    caption_lines: list[str] = field(default_factory=list)
    color_tokens: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ImageSnapshotReferencePayload:
    snapshot_id: str
    title: str
    image_url: str
    source_url: str
    note: str = ""


@dataclass(slots=True)
class SceneImageGenerationRequestPayload:
    project_id: str
    scene_id: str
    scene_title: str
    scene_description: str
    base_image_prompt: str
    character_profile: CharacterProfilePayload
    project_locked_character: bool = False
    layout: KoreanInfographicLayoutPayload | None = None
    reference_snapshots: list[ImageSnapshotReferencePayload] = field(default_factory=list)
    user_instructions: str = ""
    prompt_override: str | None = None
    previous_asset_url: str | None = None


@dataclass(slots=True)
class ClaudeMessagesRequestPayload:
    model: str
    system_prompt: str
    user_prompt: str
    max_tokens: int
    temperature: float = 0.2
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ClaudeMessagesResponsePayload:
    model: str
    raw_text: str
    stop_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass(slots=True)
class ScriptGenerationRequestPayload:
    issue_title: str
    issue_summary: str
    verified_statistics: list[ScriptEvidencePayload] = field(default_factory=list)
    market_context: list[ScriptEvidencePayload] = field(default_factory=list)
    user_instructions: str = ""
    style_preset: str = "설명형"
    tone: str = "차분한 분석형"
    audience: str = "대중"
    prompt: ClaudeMessagesRequestPayload | None = None


@dataclass(slots=True)
class SectionRegenerationRequestPayload:
    script_title: str
    target_section_id: str
    target_section_heading: str
    target_section_content: str
    other_sections: list[ScriptSectionPayload] = field(default_factory=list)
    verified_statistics: list[ScriptEvidencePayload] = field(default_factory=list)
    market_context: list[ScriptEvidencePayload] = field(default_factory=list)
    user_instructions: str = ""
    style_preset: str = "설명형"
    tone: str = "차분한 분석형"
    audience: str = "대중"
    prompt: ClaudeMessagesRequestPayload | None = None


@dataclass(slots=True)
class ScriptGenerationPayload:
    title: str
    summary: str
    outline: list[str]
    sections: list[ScriptSectionPayload] = field(default_factory=list)
    scenes: list[ScriptScenePayload] = field(default_factory=list)
    evidence_mappings: list[ScriptEvidenceMappingPayload] = field(default_factory=list)
    raw_response_text: str = ""
    provider_model: str | None = None
    stop_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass(slots=True)
class ImageGenerationPayload:
    scene_id: str
    prompt: str
    asset_url: str
    thumbnail_url: str
    revised_prompt: str = ""
    provider_name: str = ""
    reference_snapshot_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class VerticalVideoInstructionsPayload:
    aspect_ratio: str = "9:16"
    duration_seconds: int = 8
    framing: str = "세로형 프레임, 인물 중심, 자막 안전영역 확보"
    caption_style: str = "굵은 한국어 자막"
    pacing: str = "steady"
    motion_emphasis: str = "medium"


@dataclass(slots=True)
class SceneVideoPreparationRequestPayload:
    project_id: str
    scene_id: str
    scene_title: str
    scene_description: str
    image_asset_id: str | None
    image_asset_url: str | None
    image_prompt: str
    motion_prompt: str
    bundle_path: str
    download_path: str
    vertical_instructions: VerticalVideoInstructionsPayload = field(default_factory=VerticalVideoInstructionsPayload)
    user_instructions: str = ""


@dataclass(slots=True)
class VideoPreparationPayload:
    scene_id: str
    prompt: str
    motion_notes: str
    bundle_path: str
    download_path: str = ""
    image_asset_id: str | None = None
    provider_name: str = ""


@dataclass(slots=True)
class VideoExecutionRequestPayload:
    project_id: str
    video_asset_id: str
    scene_id: str
    bundle_path: str
    user_instructions: str = ""


@dataclass(slots=True)
class VideoExecutionPayload:
    video_asset_id: str
    scene_id: str
    provider_job_id: str
    status: str
    output_path: str
    bundle_path: str
    provider_name: str = ""


class NewsProviderPort(Protocol):
    provider_name: str

    def fetch_latest(self, keyword: str | None = None) -> list[NewsArticlePayload]:
        ...


class StatisticsProviderPort(Protocol):
    provider_name: str
    source_url: str

    def search_indicators(self, keyword: str) -> list[IndicatorPayload]:
        ...

    def recommend_indicators(self, issue_title: str) -> list[IndicatorPayload]:
        ...

    def get_indicator(self, indicator_code: str) -> IndicatorPayload | None:
        ...

    def get_time_series(self, indicator_code: str) -> list[TimeSeriesPointPayload]:
        ...


class EcosProviderPort(StatisticsProviderPort, Protocol):
    ...


class KosisProviderPort(StatisticsProviderPort, Protocol):
    ...


class FredProviderPort(StatisticsProviderPort, Protocol):
    ...


class OecdProviderPort(StatisticsProviderPort, Protocol):
    ...


class MarketDataProviderPort(Protocol):
    provider_name: str
    source_url: str

    def search_assets(self, query: str, asset_class: str | None = None) -> list[MarketQuotePayload]:
        ...

    def get_asset(self, symbol: str) -> MarketQuotePayload | None:
        ...

    def get_time_series(self, symbol: str) -> list[TimeSeriesPointPayload]:
        ...


class YahooFinanceProviderPort(MarketDataProviderPort, Protocol):
    ...


class InvestingProviderPort(MarketDataProviderPort, Protocol):
    ...


class SeekingAlphaProviderPort(MarketDataProviderPort, Protocol):
    ...


class SnapshotProviderPort(Protocol):
    provider_name: str
    mode: str
    integration_boundary_note: str

    def capture(self, url: str, note: str = "", source_title: str | None = None) -> SnapshotPayload:
        ...


class ScriptModelPort(Protocol):
    provider_name: str
    mode: str

    def generate_script(self, payload: ScriptGenerationRequestPayload) -> ScriptGenerationPayload:
        ...

    def regenerate_section(self, payload: SectionRegenerationRequestPayload) -> ScriptSectionPayload:
        ...


class ClaudeMessagesProviderPort(ScriptModelPort, Protocol):
    def create_message(self, payload: ClaudeMessagesRequestPayload) -> ClaudeMessagesResponsePayload:
        ...


class ImageGenerationPort(Protocol):
    provider_name: str
    mode: str

    def generate_image(self, payload: SceneImageGenerationRequestPayload) -> ImageGenerationPayload:
        ...

    def edit_image(self, payload: SceneImageGenerationRequestPayload) -> ImageGenerationPayload:
        ...


class VideoWorkflowPort(Protocol):
    provider_name: str
    mode: str

    def prepare_scene(self, payload: SceneVideoPreparationRequestPayload) -> VideoPreparationPayload:
        ...

    def execute_bundle(self, payload: VideoExecutionRequestPayload) -> VideoExecutionPayload:
        ...


class VeoWorkflowPort(VideoWorkflowPort, Protocol):
    ...
