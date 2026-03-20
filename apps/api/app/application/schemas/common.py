from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MessageResponse(APIModel):
    message: str


class PaginationMeta(APIModel):
    total: int
    page: int = 1
    page_size: int = 20


class SourceMetadata(APIModel):
    source_name: str
    source_url: str
    captured_at: datetime | None = None
    note: str | None = None


class EvidenceReference(APIModel):
    evidence_id: str
    source_kind: str
    label: str
    indicator_code: str | None = None
    release_date: str | None = None
    value: float | None = None
    source: SourceMetadata


class JobLogEntry(APIModel):
    timestamp: datetime
    level: str
    message: str


class JobSummary(APIModel):
    id: str
    job_type: str
    status: str
    project_id: str
    created_at: datetime
    updated_at: datetime

