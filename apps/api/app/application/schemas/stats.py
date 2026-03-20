from __future__ import annotations

from pydantic import Field

from app.application.schemas.common import APIModel, EvidenceReference, SourceMetadata


class StatisticSeriesPoint(APIModel):
    date: str
    value: float


class StatisticSummary(APIModel):
    id: str
    indicator_code: str
    name: str
    source_name: str
    source_url: str
    description: str
    latest_value: float
    previous_value: float | None = None
    frequency: str
    release_date: str
    unit: str
    recommended_reason: str | None = None
    tags: list[str] = Field(default_factory=list)
    stale: bool = False
    series_preview: list[StatisticSeriesPoint] = Field(default_factory=list)


class RecommendStatisticRequest(APIModel):
    project_id: str
    issue_id: str
    user_instructions: str | None = None


class SearchStatisticRequest(APIModel):
    keyword: str
    source_scope: list[str] = Field(default_factory=lambda: ["ECOS", "KOSIS", "FRED", "OECD"])


class StatisticListResponse(APIModel):
    items: list[StatisticSummary]


class StatisticSeriesResponse(APIModel):
    indicator_code: str
    source_name: str | None = None
    unit: str | None = None
    frequency: str | None = None
    items: list[StatisticSeriesPoint]


class EvidenceContextRequest(APIModel):
    project_id: str
    indicator_codes: list[str] = Field(default_factory=list)
    market_symbols: list[str] = Field(default_factory=list)
    freshness_threshold_days: int = 45


class EvidenceContextItem(APIModel):
    source_kind: str
    label: str
    summary: str
    indicator_code: str | None = None
    release_date: str | None = None
    value: float | None = None
    stale: bool = False
    source: SourceMetadata


class EvidenceContextResponse(APIModel):
    project_id: str
    combined_context: str
    items: list[EvidenceContextItem]


class FactCheckRequest(APIModel):
    project_id: str
    claims: list[str]
    evidence_ids: list[str] = Field(default_factory=list)


class FactCheckItem(APIModel):
    claim: str
    supported: bool
    warnings: list[str] = Field(default_factory=list)
    evidences: list[EvidenceReference] = Field(default_factory=list)


class FactCheckResponse(APIModel):
    items: list[FactCheckItem]
