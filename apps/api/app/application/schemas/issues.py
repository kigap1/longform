from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.application.schemas.common import APIModel, PaginationMeta


class ArticleSummary(APIModel):
    id: str
    title: str
    source_name: str
    published_at: datetime
    url: str
    summary: str


class IssueSummaryCard(APIModel):
    id: str
    title: str
    category: str
    priority_score: float
    reasons: list[str] = Field(default_factory=list)
    related_articles: list[ArticleSummary] = Field(default_factory=list)


class IssueListResponse(APIModel):
    items: list[IssueSummaryCard]
    meta: PaginationMeta


class IssueRankRequest(APIModel):
    project_id: str | None = None
    category: str | None = None
    keywords: list[str] = Field(default_factory=list)


class IssueRankResponse(APIModel):
    items: list[IssueSummaryCard]

