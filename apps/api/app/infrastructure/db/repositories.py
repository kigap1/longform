from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db import models


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class ProjectRepository:
    session: Session

    def list_all(self) -> list[models.Project]:
        stmt = select(models.Project).order_by(desc(models.Project.updated_at))
        return list(self.session.scalars(stmt))

    def get(self, project_id: str) -> models.Project | None:
        stmt = (
            select(models.Project)
            .where(models.Project.id == project_id)
            .options(selectinload(models.Project.issues), selectinload(models.Project.evidences))
        )
        return self.session.scalar(stmt)

    def first(self) -> models.Project | None:
        stmt = select(models.Project).order_by(models.Project.created_at.asc()).limit(1)
        return self.session.scalar(stmt)

    def create(self, *, name: str, description: str, issue_focus: str | None) -> models.Project:
        project = models.Project(name=name, description=description, issue_focus=issue_focus)
        self.session.add(project)
        self.session.flush()
        return project


@dataclass(slots=True)
class AppSettingRepository:
    session: Session

    def list_all(self) -> list[models.AppSetting]:
        stmt = select(models.AppSetting).order_by(models.AppSetting.category.asc(), models.AppSetting.key.asc())
        return list(self.session.scalars(stmt))

    def get(self, *, category: str, key: str) -> models.AppSetting | None:
        stmt = select(models.AppSetting).where(
            models.AppSetting.category == category,
            models.AppSetting.key == key,
        )
        return self.session.scalar(stmt)

    def upsert(self, *, category: str, key: str, value: str, secret: bool) -> models.AppSetting:
        stmt = select(models.AppSetting).where(
            models.AppSetting.category == category,
            models.AppSetting.key == key,
        )
        setting = self.session.scalar(stmt)
        if setting is None:
            setting = models.AppSetting(category=category, key=key, value=value, secret=secret)
            self.session.add(setting)
        else:
            setting.value = value
            setting.secret = secret
        self.session.flush()
        return setting


@dataclass(slots=True)
class IssueRepository:
    session: Session

    def list_by_project(self, project_id: str) -> list[models.Issue]:
        stmt = (
            select(models.Issue)
            .where(models.Issue.project_id == project_id)
            .options(selectinload(models.Issue.articles))
            .order_by(desc(models.Issue.priority_score))
        )
        return list(self.session.scalars(stmt))

    def get(self, issue_id: str) -> models.Issue | None:
        stmt = select(models.Issue).where(models.Issue.id == issue_id)
        return self.session.scalar(stmt)

    def replace_for_project(self, *, project_id: str, issue_cards: list[dict]) -> list[models.Issue]:
        existing = self.list_by_project(project_id)
        for issue in existing:
            self.session.delete(issue)
        self.session.flush()

        created: list[models.Issue] = []
        for card in issue_cards:
            issue = models.Issue(
                project_id=project_id,
                title=card["title"],
                category=card["category"],
                summary=card.get("summary", ""),
                priority_score=card["priority_score"],
                ranking_reasons=card["reasons"],
            )
            self.session.add(issue)
            self.session.flush()
            for article in card["related_articles"]:
                raw_payload = dict(article)
                published_at = raw_payload.get("published_at")
                if isinstance(published_at, datetime):
                    raw_payload["published_at"] = published_at.isoformat()
                self.session.add(
                    models.Article(
                        issue_id=issue.id,
                        title=article["title"],
                        source_name=article["source_name"],
                        url=article["url"],
                        published_at=article["published_at"],
                        summary=article["summary"],
                        credibility_score=article.get("credibility_score", 0.7),
                        raw_payload=raw_payload,
                    )
                )
            created.append(issue)

        self.session.flush()
        return created


@dataclass(slots=True)
class StatisticRepository:
    session: Session

    def list_by_project(self, project_id: str) -> list[models.Statistic]:
        stmt = select(models.Statistic).where(models.Statistic.project_id == project_id).order_by(models.Statistic.created_at.asc())
        return list(self.session.scalars(stmt))

    def get_many(self, statistic_ids: list[str]) -> list[models.Statistic]:
        if not statistic_ids:
            return []
        stmt = select(models.Statistic).where(models.Statistic.id.in_(statistic_ids)).order_by(models.Statistic.created_at.asc())
        return list(self.session.scalars(stmt))

    def replace_for_project(self, *, project_id: str, statistics: list[dict]) -> list[models.Statistic]:
        self.session.execute(delete(models.Statistic).where(models.Statistic.project_id == project_id))
        self.session.flush()
        rows: list[models.Statistic] = []
        for item in statistics:
            row = models.Statistic(
                project_id=project_id,
                indicator_code=item["indicator_code"],
                name=item["name"],
                source_name=item["source_name"],
                latest_value=item["latest_value"],
                previous_value=item["previous_value"],
                frequency=item["frequency"],
                release_date=item["release_date"],
                unit=item["unit"],
                stale=item["stale"],
                series_payload=item["series_payload"],
            )
            self.session.add(row)
            rows.append(row)
        self.session.flush()
        return rows


@dataclass(slots=True)
class SnapshotRepository:
    session: Session

    def create(
        self,
        *,
        project_id: str,
        title: str,
        source_url: str,
        image_url: str,
        note: str,
        captured_at: str,
        source_title: str = "",
    ) -> models.Snapshot:
        snapshot = models.Snapshot(
            project_id=project_id,
            title=title,
            source_url=source_url,
            image_url=image_url,
            note=note,
            captured_at=captured_at,
            source_title=source_title,
        )
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def get(self, snapshot_id: str) -> models.Snapshot | None:
        stmt = select(models.Snapshot).where(models.Snapshot.id == snapshot_id)
        return self.session.scalar(stmt)

    def list_by_project(self, project_id: str | None = None) -> list[models.Snapshot]:
        stmt = select(models.Snapshot).order_by(desc(models.Snapshot.created_at))
        if project_id is not None:
            stmt = stmt.where(models.Snapshot.project_id == project_id)
        return list(self.session.scalars(stmt))

    def get_many(self, snapshot_ids: list[str]) -> list[models.Snapshot]:
        if not snapshot_ids:
            return []
        stmt = select(models.Snapshot).where(models.Snapshot.id.in_(snapshot_ids))
        rows = list(self.session.scalars(stmt))
        order = {snapshot_id: index for index, snapshot_id in enumerate(snapshot_ids)}
        return sorted(rows, key=lambda item: order.get(item.id, len(order)))


@dataclass(slots=True)
class EvidenceRepository:
    session: Session

    def list_by_project(self, project_id: str) -> list[models.Evidence]:
        stmt = select(models.Evidence).where(models.Evidence.project_id == project_id).order_by(models.Evidence.created_at.asc())
        return list(self.session.scalars(stmt))

    def create_many(self, *, project_id: str, items: list[dict]) -> list[models.Evidence]:
        created: list[models.Evidence] = []
        for item in items:
            evidence = models.Evidence(
                project_id=project_id,
                source_kind=item["source_kind"],
                label=item["label"],
                source_name=item["source_name"],
                source_url=item["source_url"],
                indicator_code=item.get("indicator_code"),
                release_date=item.get("release_date"),
                value=item.get("value"),
                status=item["status"],
                note=item.get("note", ""),
                metadata_json=item.get("metadata_json", {}),
            )
            self.session.add(evidence)
            created.append(evidence)
        self.session.flush()
        return created


@dataclass(slots=True)
class CharacterRepository:
    session: Session

    def list_by_project(self, project_id: str) -> list[models.CharacterProfile]:
        stmt = select(models.CharacterProfile).where(models.CharacterProfile.project_id == project_id)
        return list(self.session.scalars(stmt))

    def get(self, character_profile_id: str) -> models.CharacterProfile | None:
        stmt = select(models.CharacterProfile).where(models.CharacterProfile.id == character_profile_id)
        return self.session.scalar(stmt)

    def get_locked_for_project(self, project_id: str) -> models.CharacterProfile | None:
        stmt = (
            select(models.CharacterProfile)
            .where(models.CharacterProfile.project_id == project_id, models.CharacterProfile.locked.is_(True))
            .order_by(models.CharacterProfile.created_at.asc())
            .limit(1)
        )
        return self.session.scalar(stmt)

    def create_many(self, *, project_id: str, items: list[dict]) -> list[models.CharacterProfile]:
        created: list[models.CharacterProfile] = []
        for item in items:
            profile = models.CharacterProfile(project_id=project_id, **item)
            self.session.add(profile)
            created.append(profile)
        self.session.flush()
        return created


@dataclass(slots=True)
class SceneRepository:
    session: Session

    def get(self, scene_id: str) -> models.Scene | None:
        stmt = (
            select(models.Scene)
            .where(models.Scene.id == scene_id)
            .options(selectinload(models.Scene.images), selectinload(models.Scene.videos))
        )
        return self.session.scalar(stmt)

    def list_by_project(self, project_id: str) -> list[models.Scene]:
        stmt = select(models.Scene).where(models.Scene.project_id == project_id).order_by(models.Scene.order_index.asc())
        return list(self.session.scalars(stmt))

    def update_image_prompt(self, *, scene_id: str, image_prompt: str) -> models.Scene:
        scene = self.get(scene_id)
        if scene is None:
            raise ValueError(f"Scene not found: {scene_id}")
        scene.image_prompt = image_prompt
        self.session.flush()
        return scene


@dataclass(slots=True)
class ScriptRepository:
    session: Session

    def get(self, script_id: str) -> models.Script | None:
        stmt = (
            select(models.Script)
            .where(models.Script.id == script_id)
            .options(selectinload(models.Script.sections))
        )
        return self.session.scalar(stmt)

    def latest_by_project(self, project_id: str) -> models.Script | None:
        stmt = (
            select(models.Script)
            .where(models.Script.project_id == project_id)
            .options(selectinload(models.Script.sections))
            .order_by(desc(models.Script.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)

    def list_scenes(self, script_id: str) -> list[models.Scene]:
        stmt = select(models.Scene).where(models.Scene.script_id == script_id).order_by(models.Scene.order_index.asc())
        return list(self.session.scalars(stmt))

    def create(
        self,
        *,
        project_id: str,
        issue_id: str | None,
        title: str,
        outline: list[str],
        hook: str,
        body: str,
        conclusion: str,
        version_number: int,
        sections: list[dict],
        scenes: list[dict],
        prompt_snapshot: dict,
    ) -> models.Script:
        script = models.Script(
            project_id=project_id,
            issue_id=issue_id,
            title=title,
            outline=outline,
            hook=hook,
            body=body,
            conclusion=conclusion,
            version_number=version_number,
            prompt_snapshot=prompt_snapshot,
        )
        self.session.add(script)
        self.session.flush()

        for section in sections:
            self.session.add(models.ScriptSection(script_id=script.id, **section))
        for scene in scenes:
            self.session.add(models.Scene(project_id=project_id, script_id=script.id, **scene))

        self.session.flush()
        self.session.refresh(script)
        return script

    def update(
        self,
        *,
        script_id: str,
        title: str,
        outline: list[str],
        hook: str,
        body: str,
        conclusion: str,
        version_number: int,
        prompt_snapshot: dict,
    ) -> models.Script:
        script = self.get(script_id)
        if script is None:
            raise ValueError(f"Script not found: {script_id}")
        script.title = title
        script.outline = outline
        script.hook = hook
        script.body = body
        script.conclusion = conclusion
        script.version_number = version_number
        script.prompt_snapshot = prompt_snapshot
        self.session.flush()
        return script

    def replace_sections(self, *, script_id: str, sections: list[dict]) -> list[models.ScriptSection]:
        script = self.get(script_id)
        if script is None:
            raise ValueError(f"Script not found: {script_id}")
        for section in list(script.sections):
            self.session.delete(section)
        self.session.flush()
        created: list[models.ScriptSection] = []
        for section in sections:
            row = models.ScriptSection(script_id=script_id, **section)
            self.session.add(row)
            created.append(row)
        self.session.flush()
        return created

    def update_section(self, *, section_id: str, content: str, evidence_ids: list[str]) -> models.ScriptSection:
        stmt = select(models.ScriptSection).where(models.ScriptSection.id == section_id)
        section = self.session.scalar(stmt)
        if section is None:
            raise ValueError(f"Script section not found: {section_id}")
        section.content = content
        section.evidence_ids = evidence_ids
        self.session.flush()
        return section

    def replace_scenes(self, *, project_id: str, script_id: str, scenes: list[dict]) -> list[models.Scene]:
        for scene in self.list_scenes(script_id):
            self.session.delete(scene)
        self.session.flush()
        created: list[models.Scene] = []
        for scene in scenes:
            row = models.Scene(project_id=project_id, script_id=script_id, **scene)
            self.session.add(row)
            created.append(row)
        self.session.flush()
        return created


@dataclass(slots=True)
class RevisionRepository:
    session: Session

    def create(
        self,
        *,
        project_id: str,
        entity_type: str,
        entity_id: str,
        version_number: int,
        snapshot_json: dict,
        change_note: str,
    ) -> models.ProjectRevision:
        revision = models.ProjectRevision(
            project_id=project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=version_number,
            snapshot_json=snapshot_json,
            change_note=change_note,
        )
        self.session.add(revision)
        self.session.flush()
        return revision


@dataclass(slots=True)
class AssetRepository:
    session: Session

    def list_images_for_scene(self, scene_id: str) -> list[models.ImageAsset]:
        stmt = select(models.ImageAsset).where(models.ImageAsset.scene_id == scene_id).order_by(desc(models.ImageAsset.created_at))
        return list(self.session.scalars(stmt))

    def latest_image_for_scene(self, scene_id: str) -> models.ImageAsset | None:
        stmt = (
            select(models.ImageAsset)
            .where(models.ImageAsset.scene_id == scene_id)
            .order_by(desc(models.ImageAsset.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)

    def get_video(self, video_asset_id: str) -> models.VideoAsset | None:
        stmt = select(models.VideoAsset).where(models.VideoAsset.id == video_asset_id)
        return self.session.scalar(stmt)

    def get_many_videos(self, video_asset_ids: list[str]) -> list[models.VideoAsset]:
        if not video_asset_ids:
            return []
        stmt = select(models.VideoAsset).where(models.VideoAsset.id.in_(video_asset_ids))
        rows = list(self.session.scalars(stmt))
        order = {video_asset_id: index for index, video_asset_id in enumerate(video_asset_ids)}
        return sorted(rows, key=lambda item: order.get(item.id, len(order)))

    def list_videos_for_scene(self, scene_id: str) -> list[models.VideoAsset]:
        stmt = select(models.VideoAsset).where(models.VideoAsset.scene_id == scene_id).order_by(desc(models.VideoAsset.created_at))
        return list(self.session.scalars(stmt))

    def create_image(
        self,
        *,
        scene_id: str,
        prompt: str,
        asset_url: str,
        thumbnail_url: str,
        status: str,
        provider_name: str,
        revision_note: str = "",
    ) -> models.ImageAsset:
        row = models.ImageAsset(
            scene_id=scene_id,
            prompt=prompt,
            asset_url=asset_url,
            thumbnail_url=thumbnail_url,
            status=status,
            provider_name=provider_name,
            revision_note=revision_note,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def create_video(
        self,
        *,
        scene_id: str,
        prompt: str,
        motion_notes: str,
        bundle_path: str,
        status: str,
        provider_name: str,
    ) -> models.VideoAsset:
        row = models.VideoAsset(
            scene_id=scene_id,
            prompt=prompt,
            motion_notes=motion_notes,
            bundle_path=bundle_path,
            status=status,
            provider_name=provider_name,
        )
        self.session.add(row)
        self.session.flush()
        return row


@dataclass(slots=True)
class JobRepository:
    session: Session

    def list_all(self, project_id: str | None = None) -> list[models.Job]:
        stmt = select(models.Job).options(selectinload(models.Job.logs)).order_by(desc(models.Job.created_at))
        if project_id is not None:
            stmt = stmt.where(models.Job.project_id == project_id)
        return list(self.session.scalars(stmt))

    def get(self, job_id: str) -> models.Job | None:
        stmt = select(models.Job).where(models.Job.id == job_id).options(selectinload(models.Job.logs))
        return self.session.scalar(stmt)

    def create(
        self,
        *,
        project_id: str,
        job_type: str,
        status: str,
        payload: dict,
        result: dict | None = None,
        error_message: str = "",
    ) -> models.Job:
        job = models.Job(
            project_id=project_id,
            job_type=job_type,
            status=status,
            payload=payload,
            result=result or {},
            error_message=error_message,
        )
        self.session.add(job)
        self.session.flush()
        return job

    def add_log(self, *, job_id: str, level: str, message: str) -> models.JobLog:
        log = models.JobLog(job_id=job_id, level=level, message=message)
        self.session.add(log)
        self.session.flush()
        return log


@dataclass(slots=True)
class RepositoryRegistry:
    session: Session

    @property
    def projects(self) -> ProjectRepository:
        return ProjectRepository(self.session)

    @property
    def settings(self) -> AppSettingRepository:
        return AppSettingRepository(self.session)

    @property
    def issues(self) -> IssueRepository:
        return IssueRepository(self.session)

    @property
    def statistics(self) -> StatisticRepository:
        return StatisticRepository(self.session)

    @property
    def snapshots(self) -> SnapshotRepository:
        return SnapshotRepository(self.session)

    @property
    def evidences(self) -> EvidenceRepository:
        return EvidenceRepository(self.session)

    @property
    def characters(self) -> CharacterRepository:
        return CharacterRepository(self.session)

    @property
    def scenes(self) -> SceneRepository:
        return SceneRepository(self.session)

    @property
    def scripts(self) -> ScriptRepository:
        return ScriptRepository(self.session)

    @property
    def revisions(self) -> RevisionRepository:
        return RevisionRepository(self.session)

    @property
    def assets(self) -> AssetRepository:
        return AssetRepository(self.session)

    @property
    def jobs(self) -> JobRepository:
        return JobRepository(self.session)
