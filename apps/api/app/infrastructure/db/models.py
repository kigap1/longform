from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
    )


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    issue_focus: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")

    issues: Mapped[list["Issue"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    statistics: Mapped[list["Statistic"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    market_data: Mapped[list["MarketData"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    snapshots: Mapped[list["Snapshot"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    evidences: Mapped[list["Evidence"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    scripts: Mapped[list["Script"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    characters: Mapped[list["CharacterProfile"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    scenes: Mapped[list["Scene"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    revisions: Mapped[list["ProjectRevision"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Issue(TimestampMixin, Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(Text, default="")
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    ranking_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)

    project: Mapped["Project"] = relationship(back_populates="issues")
    articles: Mapped[list["Article"]] = relationship(back_populates="issue", cascade="all, delete-orphan")


class Article(TimestampMixin, Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    issue_id: Mapped[str] = mapped_column(ForeignKey("issues.id"))
    title: Mapped[str] = mapped_column(String(255))
    source_name: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(500))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(Text, default="")
    credibility_score: Mapped[float] = mapped_column(Float, default=0.5)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    issue: Mapped["Issue"] = relationship(back_populates="articles")


class Statistic(TimestampMixin, Base):
    __tablename__ = "statistics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    indicator_code: Mapped[str] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(255))
    source_name: Mapped[str] = mapped_column(String(100))
    latest_value: Mapped[float] = mapped_column(Float)
    previous_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    frequency: Mapped[str] = mapped_column(String(30))
    release_date: Mapped[str] = mapped_column(String(30))
    unit: Mapped[str] = mapped_column(String(60))
    stale: Mapped[bool] = mapped_column(Boolean, default=False)
    series_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    project: Mapped["Project"] = relationship(back_populates="statistics")


class MarketData(TimestampMixin, Base):
    __tablename__ = "market_data"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    symbol: Mapped[str] = mapped_column(String(60), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    asset_class: Mapped[str] = mapped_column(String(60))
    source_name: Mapped[str] = mapped_column(String(100))
    latest_value: Mapped[float] = mapped_column(Float)
    change_percent: Mapped[float] = mapped_column(Float)
    as_of: Mapped[str] = mapped_column(String(40))
    chart_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    project: Mapped["Project"] = relationship(back_populates="market_data")


class Snapshot(TimestampMixin, Base):
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(String(500))
    image_url: Mapped[str] = mapped_column(String(500))
    note: Mapped[str] = mapped_column(Text, default="")
    captured_at: Mapped[str] = mapped_column(String(40))
    source_title: Mapped[str] = mapped_column(String(255), default="")

    project: Mapped["Project"] = relationship(back_populates="snapshots")


class Evidence(TimestampMixin, Base):
    __tablename__ = "evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    source_kind: Mapped[str] = mapped_column(String(50))
    label: Mapped[str] = mapped_column(String(255))
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(String(500))
    indicator_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    release_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    note: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    project: Mapped["Project"] = relationship(back_populates="evidences")


class Script(TimestampMixin, Base):
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    issue_id: Mapped[str | None] = mapped_column(ForeignKey("issues.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    outline: Mapped[list[str]] = mapped_column(JSON, default=list)
    hook: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    conclusion: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    prompt_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)

    project: Mapped["Project"] = relationship(back_populates="scripts")
    sections: Mapped[list["ScriptSection"]] = relationship(back_populates="script", cascade="all, delete-orphan")


class ScriptSection(TimestampMixin, Base):
    __tablename__ = "script_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    script_id: Mapped[str] = mapped_column(ForeignKey("scripts.id"))
    heading: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    script: Mapped["Script"] = relationship(back_populates="sections")


class CharacterProfile(TimestampMixin, Base):
    __tablename__ = "character_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    prompt_template: Mapped[str] = mapped_column(Text)
    style_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    reference_assets: Mapped[list[str]] = mapped_column(JSON, default=list)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)

    project: Mapped["Project"] = relationship(back_populates="characters")


class Scene(TimestampMixin, Base):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    script_id: Mapped[str | None] = mapped_column(ForeignKey("scripts.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    image_prompt: Mapped[str] = mapped_column(Text, default="")
    motion_prompt: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="scenes")
    images: Mapped[list["ImageAsset"]] = relationship(back_populates="scene", cascade="all, delete-orphan")
    videos: Mapped[list["VideoAsset"]] = relationship(back_populates="scene", cascade="all, delete-orphan")


class ImageAsset(TimestampMixin, Base):
    __tablename__ = "image_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"))
    prompt: Mapped[str] = mapped_column(Text)
    asset_url: Mapped[str] = mapped_column(String(500))
    thumbnail_url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    provider_name: Mapped[str] = mapped_column(String(120), default="mock-image")
    revision_note: Mapped[str] = mapped_column(Text, default="")

    scene: Mapped["Scene"] = relationship(back_populates="images")


class VideoAsset(TimestampMixin, Base):
    __tablename__ = "video_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"))
    prompt: Mapped[str] = mapped_column(Text)
    motion_notes: Mapped[str] = mapped_column(Text, default="")
    bundle_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    provider_name: Mapped[str] = mapped_column(String(120), default="mock-veo")

    scene: Mapped["Scene"] = relationship(back_populates="videos")


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    job_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str] = mapped_column(Text, default="")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="jobs")
    logs: Mapped[list["JobLog"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobLog(Base):
    __tablename__ = "job_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    level: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)

    job: Mapped["Job"] = relationship(back_populates="logs")


class ProjectRevision(TimestampMixin, Base):
    __tablename__ = "project_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    snapshot_json: Mapped[dict] = mapped_column(JSON, default=dict)
    change_note: Mapped[str] = mapped_column(Text, default="")

    project: Mapped["Project"] = relationship(back_populates="revisions")


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(80), index=True)
    key: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[str] = mapped_column(Text)
    secret: Mapped[bool] = mapped_column(Boolean, default=False)
