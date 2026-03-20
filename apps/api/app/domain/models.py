from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.enums import AssetStatus, EvidenceStatus, IssueCategory, JobStatus, JobType, ScriptStatus, SourceKind


@dataclass(slots=True)
class Article:
    id: str
    issue_id: str
    title: str
    source_name: str
    url: str
    published_at: datetime
    summary: str
    credibility_score: float
    cluster_key: str | None = None


@dataclass(slots=True)
class Issue:
    id: str
    project_id: str
    title: str
    category: IssueCategory
    summary: str
    priority_score: float = 0.0
    ranking_reasons: list[str] = field(default_factory=list)
    related_articles: list[Article] = field(default_factory=list)


@dataclass(slots=True)
class StatisticPoint:
    date_label: str
    value: float


@dataclass(slots=True)
class Statistic:
    id: str
    project_id: str
    indicator_code: str
    name: str
    source_name: str
    latest_value: float
    release_date: date
    frequency: str
    unit: str
    previous_value: float | None = None
    series_points: list[StatisticPoint] = field(default_factory=list)

    def is_stale(self, *, today: date, freshness_threshold_days: int) -> bool:
        return (today - self.release_date).days > freshness_threshold_days


@dataclass(slots=True)
class MarketDataPoint:
    date_label: str
    value: float


@dataclass(slots=True)
class MarketData:
    id: str
    project_id: str
    symbol: str
    display_name: str
    asset_class: str
    source_name: str
    latest_value: float
    change_percent: float
    as_of: datetime
    series_points: list[MarketDataPoint] = field(default_factory=list)


@dataclass(slots=True)
class Snapshot:
    id: str
    project_id: str
    title: str
    source_url: str
    image_url: str
    captured_at: datetime
    note: str = ""
    source_title: str = ""


@dataclass(slots=True)
class Evidence:
    id: str
    project_id: str
    source_kind: SourceKind
    label: str
    source_name: str
    source_url: str
    status: EvidenceStatus
    indicator_code: str | None = None
    release_date: date | None = None
    value: float | None = None
    note: str = ""
    metadata: dict[str, str | float | int | bool] = field(default_factory=dict)

    def supports_numeric_claim(self) -> bool:
        return self.indicator_code is not None and self.release_date is not None and self.value is not None


@dataclass(slots=True)
class ScriptSection:
    id: str
    heading: str
    content: str
    order_index: int
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Scene:
    id: str
    project_id: str
    title: str
    description: str
    order_index: int
    image_prompt: str
    motion_prompt: str
    reference_snapshot_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Script:
    id: str
    project_id: str
    issue_id: str | None
    title: str
    status: ScriptStatus
    outline: list[str] = field(default_factory=list)
    hook: str = ""
    body: str = ""
    conclusion: str = ""
    version_number: int = 1
    sections: list[ScriptSection] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    prompt_snapshot: dict[str, str] = field(default_factory=dict)

    def all_evidence_ids(self) -> list[str]:
        evidence_ids: list[str] = []
        for section in self.sections:
            evidence_ids.extend(section.evidence_ids)
        return evidence_ids


@dataclass(slots=True)
class CharacterProfile:
    id: str
    project_id: str
    name: str
    description: str
    prompt_template: str
    style_rules: list[str] = field(default_factory=list)
    reference_assets: list[str] = field(default_factory=list)
    locked: bool = False


@dataclass(slots=True)
class ImageAsset:
    id: str
    scene_id: str
    prompt: str
    asset_url: str
    thumbnail_url: str
    status: AssetStatus
    provider_name: str
    revision_note: str = ""


@dataclass(slots=True)
class VideoAsset:
    id: str
    scene_id: str
    prompt: str
    motion_notes: str
    bundle_path: str
    status: AssetStatus
    provider_name: str


@dataclass(slots=True)
class JobLog:
    timestamp: datetime
    level: str
    message: str


@dataclass(slots=True)
class Job:
    id: str
    project_id: str
    job_type: JobType
    status: JobStatus
    payload: dict[str, str | int | float | bool | list[str] | dict[str, str]]
    result: dict[str, str | int | float | bool | list[str] | dict[str, str]] = field(default_factory=dict)
    error_message: str = ""
    retry_count: int = 0
    logs: list[JobLog] = field(default_factory=list)

    def can_retry(self, *, max_retries: int) -> bool:
        return self.status == JobStatus.FAILED and self.retry_count < max_retries


@dataclass(slots=True)
class AppSetting:
    id: str
    category: str
    key: str
    value: str
    secret: bool = False


@dataclass(slots=True)
class ProjectRevision:
    id: str
    project_id: str
    entity_type: str
    entity_id: str
    version_number: int
    snapshot_json: dict[str, object]
    change_note: str = ""
    created_at: datetime | None = None


@dataclass(slots=True)
class Project:
    id: str
    name: str
    description: str
    issue_focus: str | None = None
    settings_ids: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    statistics: list[Statistic] = field(default_factory=list)
    market_data_items: list[MarketData] = field(default_factory=list)
    snapshots: list[Snapshot] = field(default_factory=list)
    evidences: list[Evidence] = field(default_factory=list)
    scripts: list[Script] = field(default_factory=list)
    characters: list[CharacterProfile] = field(default_factory=list)
    image_assets: list[ImageAsset] = field(default_factory=list)
    video_assets: list[VideoAsset] = field(default_factory=list)
    jobs: list[Job] = field(default_factory=list)
    revisions: list[ProjectRevision] = field(default_factory=list)
