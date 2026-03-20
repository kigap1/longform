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
    country: str | None = None
    region: str | None = None
    popularity_score: float | None = None
    credibility_score: float | None = None


class IssueSummaryCard(APIModel):
    id: str
    title: str
    category: str
    priority_score: float
    reasons: list[str] = Field(default_factory=list)
    summary: str | None = None
    article_count: int | None = None
    regions: list[str] = Field(default_factory=list)
    top_sources: list[str] = Field(default_factory=list)
    suggested_angles: list[str] = Field(default_factory=list)
    why_now: str | None = None
    related_articles: list[ArticleSummary] = Field(default_factory=list)


class IssueListResponse(APIModel):
    items: list[IssueSummaryCard]
    meta: PaginationMeta


class IssueRankRequest(APIModel):
    project_id: str | None = None
    category: str | None = None
    keywords: list[str] = Field(default_factory=list)
    user_instructions: str | None = None


class IssueRankResponse(APIModel):
    items: list[IssueSummaryCard]
