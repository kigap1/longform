from __future__ import annotations

from pydantic import Field

from app.application.schemas.common import APIModel, EvidenceReference, SourceMetadata


class MarketSeriesPoint(APIModel):
    date: str
    value: float


class MarketDataSummary(APIModel):
    id: str
    symbol: str
    display_name: str
    asset_class: str
    source_name: str
    source_url: str
    latest_value: float
    change_percent: float
    as_of: str
    currency: str
    note: str | None = None
    tags: list[str] = Field(default_factory=list)
    supplementary: bool = True
    chart_points: list[MarketSeriesPoint] = Field(default_factory=list)
    source: SourceMetadata


class MarketSearchRequest(APIModel):
    query: str
    asset_class: str | None = None
    source_scope: list[str] = Field(default_factory=lambda: ["Yahoo Finance", "Investing.com", "Seeking Alpha"])


class MarketSearchResponse(APIModel):
    items: list[MarketDataSummary]


class MarketSeriesResponse(APIModel):
    symbol: str
    source_name: str | None = None
    asset_class: str | None = None
    currency: str | None = None
    points: list[MarketSeriesPoint]


class SnapshotCaptureRequest(APIModel):
    project_id: str
    source_url: str
    source_title: str | None = None
    note: str | None = None
    attach_as_evidence: bool = True
    evidence_label: str | None = None


class SnapshotSummary(APIModel):
    id: str
    project_id: str
    title: str
    source_title: str
    image_url: str
    preview_url: str
    source_url: str
    captured_at: str
    capture_mode: str = "stub"
    integration_boundary_note: str | None = None
    note: str | None = None
    attached_evidences: list[EvidenceReference] = Field(default_factory=list)


class SnapshotListResponse(APIModel):
    items: list[SnapshotSummary]
