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
