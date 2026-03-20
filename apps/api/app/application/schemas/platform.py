from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.application.schemas.common import APIModel, JobLogEntry, JobSummary
from app.application.schemas.common import EvidenceReference


class ProjectSummary(APIModel):
    id: str
    name: str
    description: str
    issue_focus: str | None = None
    updated_at: datetime


class ProjectListResponse(APIModel):
    items: list[ProjectSummary]


class ProjectCreateRequest(APIModel):
    name: str
    description: str = ""
    issue_focus: str | None = None


class AppSettingSummary(APIModel):
    category: str
    key: str
    value: str
    secret: bool = False


class AppSettingsResponse(APIModel):
    items: list[AppSettingSummary]


class AppSettingUpsertRequest(APIModel):
    category: str
    key: str
    value: str
    secret: bool = False


class AIProviderFieldSummary(APIModel):
    key: str
    label: str
    placeholder: str
    secret: bool = False
    configured: bool = False


class AIProviderStageSupportSummary(APIModel):
    stage: str
    supported: bool
    mock_available: bool
    real_available: bool
    default_mode: str = "mock"
    note: str = ""
    default_selected: bool = False


class AIProviderSummary(APIModel):
    id: str
    label: str
    description: str
    order: int
    configured: bool = False
    fields: list[AIProviderFieldSummary] = Field(default_factory=list)
    stages: list[AIProviderStageSupportSummary] = Field(default_factory=list)


class AIProviderCatalogResponse(APIModel):
    items: list[AIProviderSummary] = Field(default_factory=list)
    defaults: dict[str, str] = Field(default_factory=dict)


class EvidenceReportSection(APIModel):
    title: str
    summary: str
    evidences: list[EvidenceReference] = Field(default_factory=list)


class EvidenceReportResponse(APIModel):
    project_id: str
    generated_at: datetime
    sections: list[EvidenceReportSection] = Field(default_factory=list)


class JobDetailResponse(APIModel):
    summary: JobSummary
    logs: list[JobLogEntry] = Field(default_factory=list)
