from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
import json
from pathlib import Path
from uuid import uuid4
import zipfile

from sqlalchemy.orm import Session

from app.application.schemas.assets import (
    CharacterListResponse,
    CharacterProfileSummary,
    ImageAssetSummary,
    ImageGenerateRequest,
    ImageRegenerateSceneRequest,
    KoreanInfographicLayoutInput,
    SceneImagePromptSummary,
    SceneImagePromptUpdateRequest,
    VideoAssetSummary,
    VideoExecutionRequest,
    VideoExecutionSummary,
    VideoPrepareRequest,
    VerticalVideoInstructionsInput,
)
from app.application.schemas.common import EvidenceReference, JobLogEntry, JobSummary, SourceMetadata
from app.application.schemas.issues import (
    ArticleSummary,
    IssueListResponse,
    IssueRankRequest,
    IssueRankResponse,
    IssueSummaryCard,
)
from app.application.schemas.market import (
    MarketDataSummary,
    MarketSeriesPoint,
    MarketSearchRequest,
    MarketSearchResponse,
    MarketSeriesResponse,
    SnapshotCaptureRequest,
    SnapshotListResponse,
    SnapshotSummary,
)
from app.application.schemas.platform import (
    AIProviderCatalogResponse,
    AIProviderFieldSummary,
    AIProviderStageSupportSummary,
    AIProviderSummary,
    AppSettingSummary,
    AppSettingsResponse,
    AppSettingUpsertRequest,
    EvidenceReportResponse,
    EvidenceReportSection,
    JobDetailResponse,
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectSummary,
)
from app.application.schemas.scripts import (
    RegenerateSectionRequest,
    RegenerateSectionResponse,
    SceneSummary,
    ScriptEvidenceMappingSummary,
    ScriptGenerationRequest,
    ScriptSectionSummary,
    ScriptSummary,
)
from app.application.schemas.stats import (
    EvidenceContextItem,
    EvidenceContextRequest,
    EvidenceContextResponse,
    FactCheckItem,
    FactCheckRequest,
    FactCheckResponse,
    RecommendStatisticRequest,
    SearchStatisticRequest,
    StatisticListResponse,
    StatisticSeriesPoint,
    StatisticSeriesResponse,
    StatisticSummary,
)
from app.application.provider_runtime import (
    AI_PROVIDER_ORDER,
    RuntimeSettingsResolver,
    normalize_provider_id,
    normalize_provider_mode,
    provider_description,
    provider_fields,
    provider_label,
    stage_support,
)
from app.domain.provider_interfaces import (
    CharacterProfilePayload,
    ImageSnapshotReferencePayload,
    ImageGenerationPort,
    InfographicStatCalloutPayload,
    KoreanInfographicLayoutPayload,
    MarketDataProviderPort,
    NewsProviderPort,
    SceneImageGenerationRequestPayload,
    SceneVideoPreparationRequestPayload,
    ScriptEvidencePayload,
    ScriptEvidenceMappingPayload,
    ScriptGenerationRequestPayload,
    ScriptSectionPayload,
    SectionRegenerationRequestPayload,
    ScriptModelPort,
    SnapshotProviderPort,
    StatisticsProviderPort,
    VerticalVideoInstructionsPayload,
    VideoExecutionRequestPayload,
    VideoWorkflowPort,
)
from app.domain.services.data_engines import MarketDataEngine, StatisticsVerificationEngine
from app.domain.services.evidence_validation import NumericClaim, validate_numeric_claims
from app.domain.services.video_prompting import build_scene_video_prompt
from app.domain.services.issue_ranking import IssueSignal, rank_issue_signals
from app.domain.services.image_prompting import build_scene_image_prompt
from app.domain.services.script_prompting import (
    build_claude_messages_request,
    build_script_generation_prompt,
    build_section_regeneration_prompt,
)
from app.core.config import get_settings
from app.infrastructure.db import models
from app.infrastructure.db.repositories import RepositoryRegistry, utcnow
from app.infrastructure.providers.adapters import (
    EcosAdapter,
    FredAdapter,
    InvestingAdapter,
    KosisAdapter,
    MockGlobalNewsAdapter,
    MockImageGeneratorAdapter,
    MockKoreanNewsAdapter,
    MockSnapshotAdapter,
    MockVeoWorkflowAdapter,
    OecdAdapter,
    SeekingAlphaAdapter,
    YahooFinanceAdapter,
)
from app.infrastructure.providers.generative_ai import build_image_provider, build_script_provider, build_video_provider
from app.infrastructure.storage.factory import build_storage


def _source(source_name: str, source_url: str, note: str | None = None) -> SourceMetadata:
    return SourceMetadata(source_name=source_name, source_url=source_url, captured_at=utcnow(), note=note)


def _to_evidence_reference(evidence: models.Evidence) -> EvidenceReference:
    return EvidenceReference(
        evidence_id=evidence.id,
        source_kind=evidence.source_kind,
        label=evidence.label,
        indicator_code=evidence.indicator_code,
        release_date=evidence.release_date,
        value=evidence.value,
        source=_source(evidence.source_name, evidence.source_url, evidence.note or None),
    )


def _default_project(repositories: RepositoryRegistry) -> models.Project:
    project = repositories.projects.first()
    if project is None:
        project = repositories.projects.create(
            name="기본 프로젝트",
            description="자동 생성된 로컬 기본 프로젝트",
            issue_focus="경제·금융·지정학",
        )
        repositories.session.commit()
    return project


def _resolve_project(repositories: RepositoryRegistry, project_id: str | None) -> models.Project:
    if project_id:
        project = repositories.projects.get(project_id)
        if project:
            return project
    return _default_project(repositories)


@dataclass(slots=True)
class ProviderRegistry:
    news: list[NewsProviderPort]
    statistics: list[StatisticsProviderPort]
    market_data: list[MarketDataProviderPort]
    snapshot: SnapshotProviderPort
    script_model: ScriptModelPort
    image_generator: ImageGenerationPort
    video_workflow: VideoWorkflowPort


def build_provider_registry(repositories: RepositoryRegistry | None = None) -> ProviderRegistry:
    runtime = RuntimeSettingsResolver(repositories)
    script_model = build_script_provider(runtime.default_provider("script"), runtime.default_mode("script"), runtime)
    image_generator = build_image_provider(runtime.default_provider("image"), runtime.default_mode("image"), runtime)
    video_workflow = build_video_provider(runtime.default_provider("video"), runtime.default_mode("video"), runtime)

    return ProviderRegistry(
        news=[MockKoreanNewsAdapter(), MockGlobalNewsAdapter()],
        statistics=[EcosAdapter(), KosisAdapter(), FredAdapter(), OecdAdapter()],
        market_data=[YahooFinanceAdapter(), InvestingAdapter(), SeekingAlphaAdapter()],
        snapshot=MockSnapshotAdapter(),
        script_model=script_model,
        image_generator=image_generator,
        video_workflow=video_workflow,
    )


@dataclass(slots=True)
class ProjectService:
    repositories: RepositoryRegistry

    def list(self) -> ProjectListResponse:
        projects = self.repositories.projects.list_all()
        return ProjectListResponse(
            items=[
                ProjectSummary(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    issue_focus=project.issue_focus,
                    updated_at=project.updated_at,
                )
                for project in projects
            ]
        )

    def create(self, payload: ProjectCreateRequest) -> ProjectSummary:
        project = self.repositories.projects.create(
            name=payload.name,
            description=payload.description,
            issue_focus=payload.issue_focus,
        )
        self.repositories.session.commit()
        return ProjectSummary(
            id=project.id,
            name=project.name,
            description=project.description,
            issue_focus=project.issue_focus,
            updated_at=project.updated_at,
        )


@dataclass(slots=True)
class SettingsService:
    repositories: RepositoryRegistry

    def list(self) -> AppSettingsResponse:
        settings = self.repositories.settings.list_all()
        return AppSettingsResponse(
            items=[
                AppSettingSummary(category=item.category, key=item.key, value=item.value, secret=item.secret)
                for item in settings
            ]
        )

    def upsert(self, payload: AppSettingUpsertRequest) -> None:
        self.repositories.settings.upsert(
            category=payload.category,
            key=payload.key,
            value=payload.value,
            secret=payload.secret,
        )
        self.repositories.session.commit()

    def ai_provider_catalog(self) -> AIProviderCatalogResponse:
        runtime = RuntimeSettingsResolver(self.repositories)
        defaults = {
            stage: runtime.default_provider(stage)
            for stage in ("script", "image", "video")
        }
        items = []
        for order, provider_id in enumerate(AI_PROVIDER_ORDER):
            fields = [
                AIProviderFieldSummary(
                    key=str(field["key"]),
                    label=str(field["label"]),
                    placeholder=str(field["placeholder"]),
                    secret=bool(field["secret"]),
                    configured=runtime.configured(str(field["key"])),
                )
                for field in provider_fields(provider_id)
            ]
            items.append(
                AIProviderSummary(
                    id=provider_id,
                    label=provider_label(provider_id),
                    description=provider_description(provider_id),
                    order=order,
                    configured=any(field.configured for field in fields),
                    fields=fields,
                    stages=[
                        AIProviderStageSupportSummary(
                            stage=stage,
                            supported=bool(stage_support(provider_id, stage)["supported"]),
                            mock_available=bool(stage_support(provider_id, stage)["mock_available"]),
                            real_available=bool(stage_support(provider_id, stage)["real_available"]),
                            default_mode=runtime.default_mode(stage),
                            note=str(stage_support(provider_id, stage)["note"]),
                            default_selected=defaults[stage] == provider_id,
                        )
                        for stage in ("script", "image", "video")
                    ],
                )
            )
        return AIProviderCatalogResponse(items=items, defaults=defaults)


@dataclass(slots=True)
class IssueService:
    repositories: RepositoryRegistry
    providers: ProviderRegistry

    def _build_cards(self, keywords: list[str] | None = None) -> list[IssueSummaryCard]:
        fetched_articles = []
        for provider in self.providers.news:
            fetched_articles.extend(provider.fetch_latest(",".join(keywords or []) or None))

        grouped: dict[str, list] = defaultdict(list)
        for article in fetched_articles:
            title = article.title.lower()
            if "oil" in title or "유가" in title or "중동" in title:
                grouped["중동 해상 물류 리스크와 유가 재상승"].append(article)
            elif "china" in title or "중국" in title or "property" in title:
                grouped["중국 부동산 경기 부진과 한국 수출 영향"].append(article)
            else:
                grouped["미국 금리 인하 기대와 원화 변동성"].append(article)

        ranked = rank_issue_signals(
            [
                IssueSignal(
                    issue_id=f"issue-{index + 1}",
                    title=title,
                    recency_hours=min((utcnow() - max(item.published_at for item in articles)).total_seconds() / 3600, 72),
                    article_count=len(articles),
                    source_credibility=round(sum(item.credibility_score for item in articles) / len(articles), 2),
                    market_impact=0.9 if "금리" in title or "유가" in title else 0.76,
                )
                for index, (title, articles) in enumerate(grouped.items())
            ]
        )

        cards: list[IssueSummaryCard] = []
        for ranked_issue in ranked:
            articles = grouped[ranked_issue.title]
            category = "economy"
            if "유가" in ranked_issue.title or "중동" in ranked_issue.title:
                category = "geopolitics"
            elif "수출" in ranked_issue.title:
                category = "investing"
            cards.append(
                IssueSummaryCard(
                    id=ranked_issue.issue_id,
                    title=ranked_issue.title,
                    category=category,
                    priority_score=ranked_issue.score,
                    reasons=ranked_issue.reasons,
                    related_articles=[
                        ArticleSummary(
                            id=str(uuid4()),
                            title=article.title,
                            source_name=article.source_name,
                            published_at=article.published_at,
                            url=article.url,
                            summary=article.summary,
                        )
                        for article in articles
                    ],
                )
            )
        return cards

    def _from_db(self, project_id: str) -> list[IssueSummaryCard]:
        persisted = self.repositories.issues.list_by_project(project_id)
        if not persisted:
            return []
        return [
            IssueSummaryCard(
                id=issue.id,
                title=issue.title,
                category=issue.category,
                priority_score=issue.priority_score,
                reasons=issue.ranking_reasons,
                related_articles=[
                    ArticleSummary(
                        id=article.id,
                        title=article.title,
                        source_name=article.source_name,
                        published_at=article.published_at,
                        url=article.url,
                        summary=article.summary,
                    )
                    for article in issue.articles
                ],
            )
            for issue in persisted
        ]

    def list_ranked(self, project_id: str | None = None) -> IssueListResponse:
        cards = self._from_db(project_id) if project_id else self._build_cards()
        if not cards:
            cards = self._build_cards()
        return IssueListResponse(items=cards, meta={"total": len(cards), "page": 1, "page_size": 20})

    def rank(self, payload: IssueRankRequest) -> IssueRankResponse:
        cards = self._build_cards(payload.keywords)
        if payload.project_id:
            project = _resolve_project(self.repositories, payload.project_id)
            self.repositories.issues.replace_for_project(
                project_id=project.id,
                issue_cards=[
                    {
                        "title": card.title,
                        "category": card.category,
                        "summary": f"{card.title} 관련 이슈 군집",
                        "priority_score": card.priority_score,
                        "reasons": list(card.reasons),
                        "related_articles": [
                            {
                                "title": article.title,
                                "source_name": article.source_name,
                                "url": article.url,
                                "published_at": article.published_at,
                                "summary": article.summary,
                                "credibility_score": 0.8,
                            }
                            for article in card.related_articles
                        ],
                    }
                    for card in cards
                ],
            )
            job = self.repositories.jobs.create(
                project_id=project.id,
                job_type="issue_discovery",
                status="success",
                payload={"keywords": payload.keywords},
                result={"issues": len(cards)},
            )
            self.repositories.jobs.add_log(job_id=job.id, level="INFO", message="이슈 랭킹 결과가 프로젝트에 저장되었습니다.")
            self.repositories.session.commit()
            return IssueRankResponse(items=self._from_db(project.id))
        return IssueRankResponse(items=cards)


@dataclass(slots=True)
class StatisticService:
    repositories: RepositoryRegistry
    providers: ProviderRegistry

    def _statistics_engine(self) -> StatisticsVerificationEngine:
        return StatisticsVerificationEngine(self.providers.statistics)

    def _market_engine(self) -> MarketDataEngine:
        return MarketDataEngine(self.providers.market_data)

    def _to_summary(self, indicator, freshness_threshold_days: int = 45) -> StatisticSummary:
        stale = self._statistics_engine().detect_stale(
            indicator.release_date,
            freshness_threshold_days=freshness_threshold_days,
            today=date.today(),
        )
        return StatisticSummary(
            id=str(uuid4()),
            indicator_code=indicator.code,
            name=indicator.name,
            source_name=indicator.source_name,
            source_url=indicator.source_url,
            description=indicator.description,
            latest_value=indicator.latest_value,
            previous_value=indicator.previous_value,
            frequency=indicator.frequency,
            release_date=indicator.release_date,
            unit=indicator.unit,
            recommended_reason=indicator.recommended_reason,
            tags=indicator.tags,
            stale=stale,
            series_preview=[
                StatisticSeriesPoint(date=point.date, value=point.value) for point in indicator.series_points[:6]
            ],
        )

    def recommend(self, payload: RecommendStatisticRequest) -> StatisticListResponse:
        issue = self.repositories.issues.get(payload.issue_id)
        issue_title = issue.title if issue else payload.issue_id
        items = self._statistics_engine().recommend_indicators(issue_title, max_items=8)
        summaries = [self._to_summary(item) for item in items[:8]]
        self.repositories.statistics.replace_for_project(
            project_id=_resolve_project(self.repositories, payload.project_id).id,
            statistics=[
                {
                    "indicator_code": item.indicator_code,
                    "name": item.name,
                    "source_name": item.source_name,
                    "latest_value": item.latest_value,
                    "previous_value": item.previous_value,
                    "frequency": item.frequency,
                    "release_date": item.release_date,
                    "unit": item.unit,
                    "stale": item.stale,
                    "series_payload": [point.model_dump() for point in item.series_preview],
                }
                for item in summaries
            ],
        )
        self.repositories.session.commit()
        return StatisticListResponse(items=summaries)

    def search(self, payload: SearchStatisticRequest) -> StatisticListResponse:
        items = self._statistics_engine().search_indicators(
            payload.keyword,
            source_scope=payload.source_scope,
            max_items=12,
        )
        return StatisticListResponse(items=[self._to_summary(item) for item in items[:12]])

    def series(self, indicator_code: str) -> StatisticSeriesResponse:
        payload = self._statistics_engine().get_time_series(indicator_code)
        if payload is None:
            return StatisticSeriesResponse(indicator_code=indicator_code, items=[])
        indicator, points = payload
        return StatisticSeriesResponse(
            indicator_code=indicator.code,
            source_name=indicator.source_name,
            unit=indicator.unit,
            frequency=indicator.frequency,
            items=[StatisticSeriesPoint(date=point.date, value=point.value) for point in points],
        )

    def evidence_context(self, payload: EvidenceContextRequest) -> EvidenceContextResponse:
        statistics_engine = self._statistics_engine()
        market_engine = self._market_engine()

        indicators = [
            item
            for item in (statistics_engine.get_indicator(indicator_code) for indicator_code in payload.indicator_codes)
            if item is not None
        ]
        market_assets = [
            item for item in (market_engine.get_asset(symbol) for symbol in payload.market_symbols) if item is not None
        ]

        context_lines, combined_context = statistics_engine.build_evidence_context(
            indicators=indicators,
            market_assets=market_assets,
            freshness_threshold_days=payload.freshness_threshold_days,
            today=date.today(),
        )

        return EvidenceContextResponse(
            project_id=_resolve_project(self.repositories, payload.project_id).id,
            combined_context=combined_context,
            items=[
                EvidenceContextItem(
                    source_kind=item.source_kind,
                    label=item.label,
                    summary=item.context_line,
                    indicator_code=item.indicator_code,
                    release_date=item.release_date,
                    value=item.value,
                    stale=item.stale,
                    source=_source(item.source_name, item.source_url),
                )
                for item in context_lines
            ],
        )

    def fact_check(self, payload: FactCheckRequest) -> FactCheckResponse:
        claims = [
            NumericClaim(
                claim_id=f"claim-{index + 1}",
                text=claim,
                indicator_code=f"IND-{index + 1}",
                value=3.25 + index,
                release_date=date.today(),
                source_name="ECOS" if index % 2 == 0 else "FRED",
            )
            for index, claim in enumerate(payload.claims)
        ]
        issues = validate_numeric_claims(claims, freshness_threshold_days=45, today=date.today())
        issues_by_claim: dict[str, list[str]] = defaultdict(list)
        for item in issues:
            issues_by_claim[item.claim_id].append(item.message)

        created = self.repositories.evidences.create_many(
            project_id=_resolve_project(self.repositories, payload.project_id).id,
            items=[
                {
                    "source_kind": "statistic",
                    "label": f"{claim.source_name} {claim.indicator_code}",
                    "source_name": claim.source_name or "Unknown",
                    "source_url": "https://example.com/evidence",
                    "indicator_code": claim.indicator_code,
                    "release_date": claim.release_date.isoformat() if claim.release_date else None,
                    "value": claim.value,
                    "status": "verified" if claim.claim_id not in issues_by_claim else "stale",
                    "note": claim.text,
                }
                for claim in claims
            ],
        )
        self.repositories.session.commit()

        return FactCheckResponse(
            items=[
                FactCheckItem(
                    claim=claim.text,
                    supported=claim.claim_id not in issues_by_claim,
                    warnings=issues_by_claim.get(claim.claim_id, []),
                    evidences=[_to_evidence_reference(created[index])],
                )
                for index, claim in enumerate(claims)
            ]
        )


@dataclass(slots=True)
class MarketService:
    providers: ProviderRegistry

    def search(self, payload: MarketSearchRequest) -> MarketSearchResponse:
        results = MarketDataEngine(self.providers.market_data).search_assets(
            payload.query,
            asset_class=payload.asset_class,
            source_scope=payload.source_scope,
            max_items=12,
        )
        return MarketSearchResponse(
            items=[
                MarketDataSummary(
                    id=str(uuid4()),
                    symbol=item.symbol,
                    display_name=item.display_name,
                    asset_class=item.asset_class,
                    source_name=item.source_name,
                    source_url=item.source_url,
                    latest_value=item.latest_value,
                    change_percent=item.change_percent,
                    as_of=item.as_of,
                    currency=item.currency,
                    note=item.note,
                    tags=item.tags,
                    chart_points=[MarketSeriesPoint(date=point.date, value=point.value) for point in item.chart_points],
                    source=_source(item.source_name, item.source_url, "보조 시장 데이터 제공자"),
                )
                for item in results[:12]
            ]
        )

    def series(self, symbol: str) -> MarketSeriesResponse:
        payload = MarketDataEngine(self.providers.market_data).get_time_series(symbol)
        if payload is None:
            return MarketSeriesResponse(symbol=symbol, points=[])
        asset, points = payload
        return MarketSeriesResponse(
            symbol=asset.symbol,
            source_name=asset.source_name,
            asset_class=asset.asset_class,
            currency=asset.currency,
            points=[MarketSeriesPoint(date=point.date, value=point.value) for point in points],
        )


@dataclass(slots=True)
class SnapshotService:
    repositories: RepositoryRegistry
    providers: ProviderRegistry

    def capture(self, payload: SnapshotCaptureRequest) -> SnapshotSummary:
        project = _resolve_project(self.repositories, payload.project_id)
        job = self.repositories.jobs.create(
            project_id=project.id,
            job_type="snapshot_capture",
            status="running",
            payload={
                "source_url": payload.source_url,
                "source_title": payload.source_title,
                "attach_as_evidence": payload.attach_as_evidence,
            },
            result={},
        )
        self.repositories.jobs.add_log(job_id=job.id, level="INFO", message="스냅샷 캡처를 시작합니다.")

        try:
            captured = self.providers.snapshot.capture(
                payload.source_url,
                payload.note or "",
                payload.source_title,
            )
            stored_image_url = self._persist_capture(
                project_id=project.id,
                payload=captured.image_bytes,
                content_type=captured.content_type,
                fallback_url=captured.image_url,
            )
            snapshot = self.repositories.snapshots.create(
                project_id=project.id,
                title=captured.title,
                source_url=captured.source_url,
                image_url=stored_image_url,
                note=captured.note,
                captured_at=captured.captured_at,
                source_title=captured.source_title,
            )
            attached_evidences = self._attach_snapshot_evidence(
                project_id=project.id,
                snapshot=snapshot,
                enabled=payload.attach_as_evidence,
                label=payload.evidence_label,
            )
            job.status = "success"
            job.result = {
                "snapshot_id": snapshot.id,
                "storage_mode": "inline" if captured.image_bytes is None else get_settings().storage_mode,
                "attached_evidence_ids": [item.id for item in attached_evidences],
            }
            self.repositories.jobs.add_log(job_id=job.id, level="INFO", message="스냅샷 메타데이터와 저장 경로를 기록했습니다.")
            if captured.integration_boundary_note:
                self.repositories.jobs.add_log(
                    job_id=job.id,
                    level="INFO",
                    message=f"Integration boundary: {captured.integration_boundary_note}",
                )
            self.repositories.session.commit()
            return self._to_summary(snapshot, attached_evidences)
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            self.repositories.jobs.add_log(job_id=job.id, level="ERROR", message=f"스냅샷 캡처 실패: {exc}")
            self.repositories.session.commit()
            raise

    def list(self, project_id: str | None = None) -> SnapshotListResponse:
        project = _resolve_project(self.repositories, project_id) if project_id else None
        items = self.repositories.snapshots.list_by_project(project.id if project else None)
        evidences_by_snapshot = self._evidences_by_snapshot(
            project.id if project else None,
            [item.id for item in items],
        )
        return SnapshotListResponse(
            items=[self._to_summary(item, evidences_by_snapshot.get(item.id, [])) for item in items]
        )

    def preview_target(self, snapshot_id: str) -> str | None:
        snapshot = self.repositories.snapshots.get(snapshot_id)
        if snapshot is None:
            return None
        return snapshot.image_url

    def _persist_capture(
        self,
        *,
        project_id: str,
        payload: bytes | None,
        content_type: str,
        fallback_url: str,
    ) -> str:
        if payload is None:
            return fallback_url
        stored = build_storage().save_bytes(
            key=f"snapshots/{project_id}/{uuid4()}{self._extension_for_content_type(content_type)}",
            payload=payload,
            content_type=content_type,
        )
        return stored.url

    def _attach_snapshot_evidence(
        self,
        *,
        project_id: str,
        snapshot: models.Snapshot,
        enabled: bool,
        label: str | None,
    ) -> list[models.Evidence]:
        if not enabled:
            return []
        created = self.repositories.evidences.create_many(
            project_id=project_id,
            items=[
                {
                    "source_kind": "snapshot",
                    "label": label or snapshot.title,
                    "source_name": self.providers.snapshot.provider_name,
                    "source_url": snapshot.source_url,
                    "status": "captured",
                    "note": snapshot.note,
                    "metadata_json": {
                        "snapshot_id": snapshot.id,
                        "preview_url": self._preview_url(snapshot.id),
                        "source_title": snapshot.source_title,
                        "capture_mode": self.providers.snapshot.mode,
                        "integration_boundary_note": self.providers.snapshot.integration_boundary_note,
                    },
                }
            ],
        )
        return created

    def _evidences_by_snapshot(
        self,
        project_id: str | None,
        snapshot_ids: list[str],
    ) -> dict[str, list[models.Evidence]]:
        if not snapshot_ids:
            return {}
        grouped: dict[str, list[models.Evidence]] = defaultdict(list)
        if project_id:
            evidence_rows = self.repositories.evidences.list_by_project(project_id)
        else:
            project_ids = {snapshot.project_id for snapshot in self.repositories.snapshots.get_many(snapshot_ids)}
            evidence_rows = []
            for current_project_id in project_ids:
                evidence_rows.extend(self.repositories.evidences.list_by_project(current_project_id))

        for evidence in evidence_rows:
            metadata = evidence.metadata_json or {}
            snapshot_id = metadata.get("snapshot_id")
            if snapshot_id in snapshot_ids:
                grouped[snapshot_id].append(evidence)
        return grouped

    def _to_summary(self, snapshot: models.Snapshot, evidences: list[models.Evidence]) -> SnapshotSummary:
        metadata = (evidences[0].metadata_json if evidences else {}) or {}
        capture_mode = metadata.get("capture_mode", self.providers.snapshot.mode)
        integration_boundary_note = metadata.get(
            "integration_boundary_note",
            self.providers.snapshot.integration_boundary_note,
        )
        return SnapshotSummary(
            id=snapshot.id,
            project_id=snapshot.project_id,
            title=snapshot.title,
            source_title=snapshot.source_title or snapshot.title,
            image_url=snapshot.image_url,
            preview_url=self._preview_url(snapshot.id),
            source_url=snapshot.source_url,
            captured_at=snapshot.captured_at,
            note=snapshot.note,
            capture_mode=capture_mode,
            integration_boundary_note=integration_boundary_note,
            attached_evidences=[_to_evidence_reference(item) for item in evidences],
        )

    def _preview_url(self, snapshot_id: str) -> str:
        return f"/api/snapshot/preview/{snapshot_id}"

    @staticmethod
    def _extension_for_content_type(content_type: str) -> str:
        mapping = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/svg+xml": ".svg",
            "application/pdf": ".pdf",
        }
        return mapping.get(content_type, ".bin")


@dataclass(slots=True)
class EvidenceService:
    repositories: RepositoryRegistry

    def report(self, project_id: str) -> EvidenceReportResponse:
        project = _resolve_project(self.repositories, project_id)
        evidences = self.repositories.evidences.list_by_project(project.id)
        grouped: dict[str, list[models.Evidence]] = defaultdict(list)
        for evidence in evidences:
            grouped[evidence.source_kind].append(evidence)

        sections = [
            EvidenceReportSection(
                title=source_kind,
                summary=f"{len(items)}건의 근거가 연결되어 있습니다.",
                evidences=[_to_evidence_reference(item) for item in items],
            )
            for source_kind, items in grouped.items()
        ]
        return EvidenceReportResponse(project_id=project.id, generated_at=utcnow(), sections=sections)


@dataclass(slots=True)
class ScriptService:
    repositories: RepositoryRegistry
    providers: ProviderRegistry

    def latest(self, project_id: str) -> ScriptSummary | None:
        project = _resolve_project(self.repositories, project_id)
        script = self.repositories.scripts.latest_by_project(project.id)
        if script is None:
            return None
        return self._summary_from_saved_script(script, project.id)

    def generate(self, payload: ScriptGenerationRequest) -> ScriptSummary:
        project = _resolve_project(self.repositories, payload.project_id)
        issue = self.repositories.issues.get(payload.issue_id)
        issue_title = issue.title if issue else payload.issue_id
        issue_summary = payload.issue_summary or (issue.summary if issue else f"{issue_title} 관련 이슈 해설")
        provider_id, provider_mode, script_model = self._select_script_provider(payload.provider_id, payload.provider_mode)
        model_name = self._resolve_model_name(payload.model_override, provider_id, script_model)
        verified_statistics, market_context = self._resolve_script_evidence_context(project.id, payload)
        prompt_build = build_script_generation_prompt(
            issue_title=issue_title,
            issue_summary=issue_summary,
            verified_statistics=verified_statistics,
            market_context=market_context,
            user_instructions=payload.user_instructions,
            style_preset=payload.style_preset,
            tone=payload.tone,
            audience=payload.audience_type,
        )
        prompt_request = build_claude_messages_request(
            model=model_name,
            build_result=prompt_build,
            max_tokens=get_settings().claude_max_tokens,
            temperature=get_settings().claude_temperature,
            metadata={
                "issue_title": issue_title,
                "primary_evidence_ids": ",".join(item.evidence_id for item in verified_statistics),
                "market_evidence_ids": ",".join(item.evidence_id for item in market_context),
            },
        )
        generated = script_model.generate_script(
            ScriptGenerationRequestPayload(
                issue_title=issue_title,
                issue_summary=issue_summary,
                verified_statistics=verified_statistics,
                market_context=market_context,
                user_instructions=payload.user_instructions,
                style_preset=payload.style_preset,
                tone=payload.tone,
                audience=payload.audience_type,
                prompt=prompt_request,
            )
        )

        sections_payload = self._section_rows(generated.sections)
        scenes_payload = self._scene_rows(generated.scenes)
        hook, body, conclusion = self._script_body_parts(generated.sections)
        prompt_snapshot = self._prompt_snapshot(
            request_payload=payload.model_dump(),
            prompt_request=prompt_request,
            verified_statistics=verified_statistics,
            market_context=market_context,
            result_title=generated.title,
            result_summary=generated.summary,
            result_outline=generated.outline,
            result_sections=generated.sections,
            result_scenes=generated.scenes,
            provider_model=generated.provider_model,
            stop_reason=generated.stop_reason,
            input_tokens=generated.input_tokens,
            output_tokens=generated.output_tokens,
            evidence_mappings=generated.evidence_mappings,
            provider_id=provider_id,
            provider_name=script_model.provider_name,
            provider_mode=provider_mode,
        )
        script = self.repositories.scripts.create(
            project_id=project.id,
            issue_id=issue.id if issue else None,
            title=generated.title,
            outline=generated.outline,
            hook=hook,
            body=body,
            conclusion=conclusion,
            version_number=1,
            sections=sections_payload,
            scenes=scenes_payload,
            prompt_snapshot=prompt_snapshot,
        )

        job = self.repositories.jobs.create(
            project_id=project.id,
            job_type="script_generation",
            status="success",
            payload={"issue_id": payload.issue_id},
            result={"script_id": script.id},
        )
        self.repositories.jobs.add_log(job_id=job.id, level="INFO", message="대본 생성과 저장이 완료되었습니다.")
        summary = self._script_summary(
            script=script,
            issue_id=issue.id if issue else None,
            project_id=project.id,
            style_preset=payload.style_preset,
            tone=payload.tone,
            audience_type=payload.audience_type,
            evidence_mappings=generated.evidence_mappings,
            provider_id=provider_id,
            provider_name=script_model.provider_name,
            provider_mode=provider_mode,
        )
        self.repositories.revisions.create(
            project_id=project.id,
            entity_type="script",
            entity_id=script.id,
            version_number=script.version_number,
            snapshot_json=summary.model_dump(mode="json"),
            change_note="초기 대본 생성",
        )
        self.repositories.session.commit()
        return summary

    def regenerate_section(self, payload: RegenerateSectionRequest) -> RegenerateSectionResponse:
        script = self.repositories.scripts.get(payload.script_id)
        if script is None:
            raise ValueError(f"Script not found: {payload.script_id}")
        sections = sorted(script.sections, key=lambda item: item.order_index)
        target = next((section for section in sections if section.id == payload.section_id), None)
        if target is None:
            raise ValueError(f"Script section not found: {payload.section_id}")

        script_snapshot = script.prompt_snapshot or {}
        snapshot_provider = script_snapshot.get("provider", {}) if isinstance(script_snapshot, dict) else {}
        fallback_provider_id = normalize_provider_id(snapshot_provider.get("id"), "openai")
        provider_id, provider_mode, script_model = self._select_script_provider(
            payload.provider_id,
            payload.provider_mode,
            fallback_provider_id=fallback_provider_id,
        )
        script_request = script_snapshot.get("request", {})
        script_result = script_snapshot.get("result", {})
        style_preset = payload.style_preset or script_request.get("style_preset", "설명형")
        tone = payload.tone or script_request.get("tone", "차분한 분석형")
        audience_type = payload.audience_type or script_request.get("audience_type", "대중")
        model_name = self._resolve_model_name(payload.model_override, provider_id, script_model)

        verified_statistics, market_context = self._resolve_existing_script_evidence(script.project_id, sections)
        prompt_build = build_section_regeneration_prompt(
            script_title=script.title,
            target_section_heading=target.heading,
            target_section_content=target.content,
            other_sections=[
                ScriptSectionPayload(heading=item.heading, content=item.content, evidence_ids=item.evidence_ids)
                for item in sections
            ],
            verified_statistics=verified_statistics,
            market_context=market_context,
            user_instructions=payload.user_instructions,
            style_preset=style_preset,
            tone=tone,
            audience=audience_type,
        )
        prompt_request = build_claude_messages_request(
            model=model_name,
            build_result=prompt_build,
            max_tokens=get_settings().claude_max_tokens,
            temperature=get_settings().claude_temperature,
            metadata={
                "issue_title": script.title,
                "primary_evidence_ids": ",".join(item.evidence_id for item in verified_statistics),
                "market_evidence_ids": ",".join(item.evidence_id for item in market_context),
            },
        )
        regenerated = script_model.regenerate_section(
            SectionRegenerationRequestPayload(
                script_title=script.title,
                target_section_id=target.id,
                target_section_heading=target.heading,
                target_section_content=target.content,
                other_sections=[
                    ScriptSectionPayload(heading=item.heading, content=item.content, evidence_ids=item.evidence_ids)
                    for item in sections
                    if item.id != target.id
                ],
                verified_statistics=verified_statistics,
                market_context=market_context,
                user_instructions=payload.user_instructions,
                style_preset=style_preset,
                tone=tone,
                audience=audience_type,
                prompt=prompt_request,
            )
        )
        updated_section = self.repositories.scripts.update_section(
            section_id=target.id,
            content=regenerated.content,
            evidence_ids=regenerated.evidence_ids,
        )
        updated_sections = sorted(script.sections, key=lambda item: item.order_index)
        section_purposes = self._snapshot_section_purposes(script_snapshot)
        regenerated_sections = [
            ScriptSectionPayload(
                heading=updated_section.heading if item.id == updated_section.id else item.heading,
                content=updated_section.content if item.id == updated_section.id else item.content,
                evidence_ids=updated_section.evidence_ids if item.id == updated_section.id else item.evidence_ids,
                narration_purpose=(
                    regenerated.narration_purpose
                    if item.id == updated_section.id
                    else section_purposes.get(item.heading, "")
                ),
            )
            for item in updated_sections
        ]
        hook, body, conclusion = self._script_body_parts(regenerated_sections)
        next_version = script.version_number + 1
        combined_evidence_mappings = self._merge_evidence_mappings(
            script_result.get("evidence_mappings") or script_snapshot.get("evidence_mappings", []),
            ScriptEvidenceMappingPayload(
                section_heading=regenerated.heading,
                evidence_ids=regenerated.evidence_ids,
                rationale=regenerated.narration_purpose,
            ),
        )
        prompt_snapshot = self._prompt_snapshot(
            request_payload=payload.model_dump(),
            prompt_request=prompt_request,
            verified_statistics=verified_statistics,
            market_context=market_context,
            result_title=script_result.get("title", script.title),
            result_summary=script_result.get("summary", ""),
            result_outline=[item.heading for item in regenerated_sections],
            result_sections=regenerated_sections,
            result_scenes=script_result.get("scenes", []),
            provider_model=model_name,
            stop_reason=None,
            input_tokens=None,
            output_tokens=None,
            evidence_mappings=combined_evidence_mappings,
            provider_id=provider_id,
            provider_name=script_model.provider_name,
            provider_mode=provider_mode,
        )
        updated_script = self.repositories.scripts.update(
            script_id=script.id,
            title=script.title,
            outline=[item.heading for item in regenerated_sections],
            hook=hook,
            body=body,
            conclusion=conclusion,
            version_number=next_version,
            prompt_snapshot=prompt_snapshot,
        )
        revision_section = ScriptSectionSummary(
            id=updated_section.id,
            heading=updated_section.heading,
            content=updated_section.content,
            evidence_ids=updated_section.evidence_ids,
            narration_purpose=regenerated.narration_purpose,
        )
        updated_summary = self._script_summary(
            script=updated_script,
            issue_id=script.issue_id,
            project_id=script.project_id,
            style_preset=style_preset,
            tone=tone,
            audience_type=audience_type,
            evidence_mappings=combined_evidence_mappings,
            provider_id=provider_id,
            provider_name=script_model.provider_name,
            provider_mode=provider_mode,
        )
        self.repositories.revisions.create(
            project_id=script.project_id,
            entity_type="script",
            entity_id=script.id,
            version_number=next_version,
            snapshot_json=updated_summary.model_dump(mode="json"),
            change_note=f"{updated_section.heading} 섹션 재생성",
        )
        self.repositories.session.commit()
        return RegenerateSectionResponse(script_id=script.id, version_number=next_version, section=revision_section)

    def _select_script_provider(
        self,
        requested_provider_id: str | None,
        requested_mode: str | None,
        *,
        fallback_provider_id: str | None = None,
    ) -> tuple[str, str, ScriptModelPort]:
        runtime = RuntimeSettingsResolver(self.repositories)
        provider_id = normalize_provider_id(
            requested_provider_id,
            normalize_provider_id(fallback_provider_id, runtime.default_provider("script")),
        )
        provider_mode = normalize_provider_mode(requested_mode, runtime.default_mode("script"))
        return provider_id, provider_mode, build_script_provider(provider_id, provider_mode, runtime)

    def _resolve_model_name(self, override: str | None, provider_id: str, script_model: ScriptModelPort) -> str:
        runtime = RuntimeSettingsResolver(self.repositories)
        model_keys = {
            "openai": "openai_model",
            "claude": "claude_model",
            "gemini": "gemini_model",
        }
        configured = runtime.get(model_keys.get(provider_id, "claude_model"))
        if script_model.mode == "real" and not (override or configured):
            raise ValueError(f"{provider_label(normalize_provider_id(provider_id))} 모델 설정이 필요합니다.")
        return override or configured or f"{provider_id}-script-mock"

    def _resolve_script_evidence_context(
        self,
        project_id: str,
        payload: ScriptGenerationRequest,
    ) -> tuple[list[ScriptEvidencePayload], list[ScriptEvidencePayload]]:
        project_evidences = self.repositories.evidences.list_by_project(project_id)
        statistics = self._resolve_statistic_evidences(project_id, payload, project_evidences)
        market = self._resolve_market_evidences(project_id, payload, project_evidences)
        return statistics, market

    def _resolve_existing_script_evidence(
        self,
        project_id: str,
        sections: list[models.ScriptSection],
    ) -> tuple[list[ScriptEvidencePayload], list[ScriptEvidencePayload]]:
        referenced_ids = {evidence_id for section in sections for evidence_id in section.evidence_ids}
        evidences = self.repositories.evidences.list_by_project(project_id)
        referenced = [item for item in evidences if item.id in referenced_ids]
        statistics = [self._to_script_evidence(item) for item in referenced if item.source_kind == "statistic"]
        market = [self._to_script_evidence(item) for item in referenced if item.source_kind == "market_data"]
        return statistics, market

    def _resolve_statistic_evidences(
        self,
        project_id: str,
        payload: ScriptGenerationRequest,
        project_evidences: list[models.Evidence],
    ) -> list[ScriptEvidencePayload]:
        selected_rows: list[ScriptEvidencePayload] = []
        evidence_by_indicator = {
            (item.source_name, item.indicator_code): item
            for item in project_evidences
            if item.source_kind == "statistic" and item.indicator_code
        }
        if payload.statistic_ids:
            for row in self.repositories.statistics.get_many(payload.statistic_ids):
                existing = evidence_by_indicator.get((row.source_name, row.indicator_code))
                if existing is not None:
                    selected_rows.append(self._to_script_evidence(existing))
                else:
                    selected_rows.append(
                        self._ensure_project_evidence(
                            project_id,
                            ScriptEvidencePayload(
                                evidence_id=f"stat:{row.indicator_code}",
                                label=row.name,
                                source_kind="statistic",
                                source_name=row.source_name,
                                source_url="https://example.com/statistics",
                                release_date=row.release_date,
                                value=row.latest_value,
                                note="프로젝트 통계 선택",
                            ),
                        )
                    )
        for indicator_code in payload.indicator_codes:
            indicator = StatisticsVerificationEngine(self.providers.statistics).get_indicator(indicator_code)
            if indicator is None:
                continue
            existing = evidence_by_indicator.get((indicator.source_name, indicator.code))
            if existing is not None:
                selected_rows.append(self._to_script_evidence(existing))
            else:
                selected_rows.append(
                    self._ensure_project_evidence(
                        project_id,
                        ScriptEvidencePayload(
                            evidence_id=f"stat:{indicator.code}",
                            label=indicator.name,
                            source_kind="statistic",
                            source_name=indicator.source_name,
                            source_url=indicator.source_url,
                            release_date=indicator.release_date,
                            value=indicator.latest_value,
                            note=indicator.description,
                        ),
                    )
                )
        if not selected_rows:
            fallback = [item for item in project_evidences if item.source_kind == "statistic"][:3]
            selected_rows = [self._to_script_evidence(item) for item in fallback]
        return self._unique_script_evidences(selected_rows)

    def _resolve_market_evidences(
        self,
        project_id: str,
        payload: ScriptGenerationRequest,
        project_evidences: list[models.Evidence],
    ) -> list[ScriptEvidencePayload]:
        _ = project_id
        selected_rows: list[ScriptEvidencePayload] = []
        evidence_by_indicator = {
            (item.source_name, item.indicator_code): item
            for item in project_evidences
            if item.source_kind == "market_data" and item.indicator_code
        }
        market_symbols = payload.market_symbols or payload.market_data_ids
        market_engine = MarketDataEngine(self.providers.market_data)
        for symbol in market_symbols:
            asset = market_engine.get_asset(symbol)
            if asset is None:
                continue
            existing = evidence_by_indicator.get((asset.source_name, asset.symbol))
            if existing is not None:
                selected_rows.append(self._to_script_evidence(existing))
            else:
                selected_rows.append(
                    self._ensure_project_evidence(
                        project_id,
                        ScriptEvidencePayload(
                            evidence_id=f"market:{asset.symbol}",
                            label=asset.display_name,
                            source_kind="market_data",
                            source_name=asset.source_name,
                            source_url=asset.source_url,
                            release_date=asset.as_of,
                            value=asset.latest_value,
                            note=asset.note,
                        ),
                    )
                )
        if not selected_rows:
            fallback = [item for item in project_evidences if item.source_kind == "market_data"][:2]
            selected_rows = [self._to_script_evidence(item) for item in fallback]
        return self._unique_script_evidences(selected_rows)

    def _to_script_evidence(self, evidence: models.Evidence) -> ScriptEvidencePayload:
        return ScriptEvidencePayload(
            evidence_id=evidence.id,
            label=evidence.label,
            source_kind=evidence.source_kind,
            source_name=evidence.source_name,
            source_url=evidence.source_url,
            release_date=evidence.release_date,
            value=evidence.value,
            note=evidence.note,
        )

    def _ensure_project_evidence(self, project_id: str, payload: ScriptEvidencePayload) -> ScriptEvidencePayload:
        created = self.repositories.evidences.create_many(
            project_id=project_id,
            items=[
                {
                    "source_kind": payload.source_kind,
                    "label": payload.label,
                    "source_name": payload.source_name,
                    "source_url": payload.source_url,
                    "indicator_code": payload.evidence_id.split(":", 1)[-1] if ":" in payload.evidence_id else payload.evidence_id,
                    "release_date": payload.release_date,
                    "value": payload.value,
                    "status": "verified" if payload.source_kind == "statistic" else "supplementary",
                    "note": payload.note,
                }
            ],
        )[0]
        return self._to_script_evidence(created)

    def _unique_script_evidences(self, items: list[ScriptEvidencePayload]) -> list[ScriptEvidencePayload]:
        unique: list[ScriptEvidencePayload] = []
        seen: set[str] = set()
        for item in items:
            if item.evidence_id in seen:
                continue
            seen.add(item.evidence_id)
            unique.append(item)
        return unique

    def _snapshot_section_purposes(self, snapshot: dict) -> dict[str, str]:
        result = snapshot.get("result", {}) if isinstance(snapshot, dict) else {}
        return {
            item.get("heading", ""): item.get("narration_purpose", "")
            for item in result.get("sections", [])
            if isinstance(item, dict)
        }

    def _merge_evidence_mappings(
        self,
        existing_mappings: list[dict] | list[ScriptEvidenceMappingPayload],
        updated_mapping: ScriptEvidenceMappingPayload,
    ) -> list[ScriptEvidenceMappingPayload]:
        normalized = [
            item
            if isinstance(item, ScriptEvidenceMappingPayload)
            else ScriptEvidenceMappingPayload(
                section_heading=item.get("section_heading", ""),
                evidence_ids=item.get("evidence_ids", []),
                rationale=item.get("rationale", ""),
            )
            for item in existing_mappings
        ]
        merged: list[ScriptEvidenceMappingPayload] = []
        replaced = False
        for item in normalized:
            if item.section_heading == updated_mapping.section_heading:
                merged.append(updated_mapping)
                replaced = True
            else:
                merged.append(item)
        if not replaced:
            merged.append(updated_mapping)
        return merged

    def _script_body_parts(self, sections: list[ScriptSectionPayload]) -> tuple[str, str, str]:
        if not sections:
            return "", "", ""
        hook = sections[0].content
        conclusion = sections[-1].content if len(sections) > 1 else sections[0].content
        middle_sections = sections[1:-1] if len(sections) > 2 else sections[1:2]
        body = "\n\n".join(section.content for section in middle_sections)
        return hook, body, conclusion

    def _section_rows(self, sections: list[ScriptSectionPayload]) -> list[dict]:
        return [
            {
                "heading": section.heading,
                "content": section.content,
                "order_index": index + 1,
                "evidence_ids": section.evidence_ids,
            }
            for index, section in enumerate(sections)
        ]

    def _scene_rows(self, scenes: list) -> list[dict]:
        return [
            {
                "title": scene.title,
                "description": scene.description,
                "image_prompt": scene.image_prompt,
                "motion_prompt": scene.motion_prompt,
                "order_index": index + 1,
            }
            for index, scene in enumerate(scenes)
        ]

    def _prompt_snapshot(
        self,
        *,
        request_payload: dict,
        prompt_request,
        verified_statistics: list[ScriptEvidencePayload],
        market_context: list[ScriptEvidencePayload],
        result_title: str,
        result_summary: str,
        result_outline: list[str],
        result_sections,
        result_scenes,
        provider_model: str | None,
        stop_reason: str | None,
        input_tokens: int | None,
        output_tokens: int | None,
        evidence_mappings,
        provider_id: str,
        provider_name: str,
        provider_mode: str,
    ) -> dict:
        serialized_sections = [asdict(item) if hasattr(item, "heading") else item for item in result_sections]
        serialized_scenes = [asdict(item) if hasattr(item, "title") else item for item in result_scenes]
        serialized_mappings = [asdict(mapping) if hasattr(mapping, "section_heading") else mapping for mapping in evidence_mappings]
        return {
            "request": request_payload,
            "provider": {
                "id": provider_id,
                "name": provider_name,
                "mode": provider_mode,
                "model": provider_model,
                "stop_reason": stop_reason,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
            "prompt": {
                "system": prompt_request.system_prompt,
                "user": prompt_request.user_prompt,
                "metadata": prompt_request.metadata,
            },
            "result": {
                "title": result_title,
                "summary": result_summary,
                "outline": result_outline,
                "sections": serialized_sections,
                "scenes": serialized_scenes,
                "evidence_mappings": serialized_mappings,
            },
            "verified_statistics": [asdict(item) for item in verified_statistics],
            "market_context": [asdict(item) for item in market_context],
            "evidence_mappings": serialized_mappings,
        }

    def _script_summary(
        self,
        *,
        script: models.Script,
        issue_id: str | None,
        project_id: str,
        style_preset: str,
        tone: str,
        audience_type: str,
        evidence_mappings,
        provider_id: str,
        provider_name: str,
        provider_mode: str,
    ) -> ScriptSummary:
        sections = sorted(script.sections, key=lambda item: item.order_index)
        snapshot_result = (script.prompt_snapshot or {}).get("result", {})
        snapshot_sections = snapshot_result.get("sections", [])
        snapshot_scenes = snapshot_result.get("scenes", [])
        narration_by_heading = {
            item.get("heading", ""): item.get("narration_purpose", "")
            for item in snapshot_sections
            if isinstance(item, dict)
        }
        scenes = self.repositories.scripts.list_scenes(script.id)
        scene_summaries = []
        for index, scene in enumerate(scenes):
            snapshot_scene = snapshot_scenes[index] if index < len(snapshot_scenes) and isinstance(snapshot_scenes[index], dict) else {}
            evidence_ids = snapshot_scene.get("evidence_ids", [])
            if not evidence_ids:
                evidence_ids = next(
                    (
                        item.get("evidence_ids", [])
                        for item in snapshot_scenes
                        if isinstance(item, dict) and item.get("title") == scene.title
                    ),
                    [],
                )
            scene_summaries.append(
                SceneSummary(
                    id=scene.id,
                    title=scene.title,
                    description=scene.description,
                    image_prompt=scene.image_prompt,
                    motion_prompt=scene.motion_prompt,
                    evidence_ids=evidence_ids,
                )
            )
        mapping_summaries = [
            ScriptEvidenceMappingSummary(**(asdict(item) if hasattr(item, "section_heading") else item))
            for item in evidence_mappings
        ]
        referenced_evidence_ids = {
            evidence_id
            for section in sections
            for evidence_id in section.evidence_ids
        }
        referenced_evidence_ids.update(
            evidence_id
            for scene in scene_summaries
            for evidence_id in scene.evidence_ids
        )
        referenced_evidence_ids.update(
            evidence_id
            for mapping in mapping_summaries
            for evidence_id in mapping.evidence_ids
        )
        all_project_evidences = self.repositories.evidences.list_by_project(project_id)
        script_evidences = (
            [item for item in all_project_evidences if item.id in referenced_evidence_ids]
            if referenced_evidence_ids
            else all_project_evidences
        )
        return ScriptSummary(
            id=script.id,
            issue_id=issue_id,
            title=script.title,
            summary=(script.prompt_snapshot or {}).get("result", {}).get("summary", ""),
            outline=script.outline,
            hook=script.hook,
            body=script.body,
            conclusion=script.conclusion,
            version_number=script.version_number,
            provider_id=provider_id,
            provider_name=provider_name,
            provider_mode=provider_mode,
            style_preset=style_preset,
            tone=tone,
            audience_type=audience_type,
            sections=[
                ScriptSectionSummary(
                    id=section.id,
                    heading=section.heading,
                    content=section.content,
                    evidence_ids=section.evidence_ids,
                    narration_purpose=narration_by_heading.get(section.heading, ""),
                )
                for section in sections
            ],
            scenes=scene_summaries,
            evidence_mappings=mapping_summaries,
            evidences=[_to_evidence_reference(item) for item in script_evidences],
        )

    def _summary_from_saved_script(self, script: models.Script, project_id: str) -> ScriptSummary:
        prompt_snapshot = script.prompt_snapshot or {}
        request_payload = prompt_snapshot.get("request", {}) if isinstance(prompt_snapshot, dict) else {}
        provider_payload = prompt_snapshot.get("provider", {}) if isinstance(prompt_snapshot, dict) else {}
        result_payload = prompt_snapshot.get("result", {}) if isinstance(prompt_snapshot, dict) else {}
        evidence_mappings = result_payload.get("evidence_mappings") or prompt_snapshot.get("evidence_mappings", [])
        provider_id = normalize_provider_id(provider_payload.get("id"), "openai")
        return self._script_summary(
            script=script,
            issue_id=script.issue_id,
            project_id=project_id,
            style_preset=request_payload.get("style_preset", ""),
            tone=request_payload.get("tone", ""),
            audience_type=request_payload.get("audience_type", ""),
            evidence_mappings=evidence_mappings,
            provider_id=provider_id,
            provider_name=provider_payload.get("name", provider_label(provider_id)),
            provider_mode=provider_payload.get("mode", "mock"),
        )


@dataclass(slots=True)
class CharacterService:
    repositories: RepositoryRegistry

    def list(self, project_id: str | None = None) -> CharacterListResponse:
        project = _resolve_project(self.repositories, project_id)
        rows = self.repositories.characters.list_by_project(project.id)
        locked = next((item for item in rows if item.locked), None)
        return CharacterListResponse(
            project_id=project.id,
            locked_character_profile_id=locked.id if locked else None,
            items=[
                CharacterProfileSummary(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    style_rules=item.style_rules,
                    prompt_template=item.prompt_template,
                    reference_assets=item.reference_assets,
                    locked=item.locked,
                )
                for item in rows
            ]
        )


@dataclass(slots=True)
class ImageService:
    repositories: RepositoryRegistry
    providers: ProviderRegistry

    def generate(self, payload: ImageGenerateRequest) -> ImageAssetSummary:
        return self._generate_scene_image(payload, regenerate=False)

    def regenerate_scene(self, payload: ImageRegenerateSceneRequest) -> ImageAssetSummary:
        return self._generate_scene_image(payload, regenerate=True)

    def update_scene_prompt(self, payload: SceneImagePromptUpdateRequest) -> SceneImagePromptSummary:
        project = _resolve_project(self.repositories, payload.project_id)
        scene = self._resolve_scene(project.id, payload.scene_id)
        updated = self.repositories.scenes.update_image_prompt(scene_id=scene.id, image_prompt=payload.prompt)
        self.repositories.revisions.create(
            project_id=project.id,
            entity_type="scene_image_prompt",
            entity_id=updated.id,
            version_number=len(self.repositories.assets.list_images_for_scene(updated.id)) + 1,
            snapshot_json={
                "scene_id": updated.id,
                "scene_title": updated.title,
                "image_prompt": updated.image_prompt,
            },
            change_note="장면 이미지 프롬프트 수동 편집",
        )
        self.repositories.session.commit()
        return SceneImagePromptSummary(scene_id=updated.id, scene_title=updated.title, image_prompt=updated.image_prompt)

    def _generate_scene_image(self, payload: ImageGenerateRequest | ImageRegenerateSceneRequest, regenerate: bool) -> ImageAssetSummary:
        project = _resolve_project(self.repositories, payload.project_id)
        scene = self._resolve_scene(project.id, payload.scene_id)
        character, project_locked = self._resolve_character(project.id, payload.character_profile_id)
        snapshots = self._resolve_snapshots(project.id, payload.reference_snapshot_ids)
        provider_id, provider_mode, image_provider = self._select_image_provider(payload.provider_id, payload.provider_mode)
        layout_input = self._resolve_layout_input(scene, payload.layout)
        latest_image = self.repositories.assets.latest_image_for_scene(scene.id)
        scene_request = SceneImageGenerationRequestPayload(
            project_id=project.id,
            scene_id=scene.id,
            scene_title=scene.title,
            scene_description=scene.description,
            base_image_prompt=payload.prompt_override or getattr(payload, "prompt", "") or scene.image_prompt or scene.description,
            character_profile=self._to_character_payload(character),
            project_locked_character=project_locked,
            layout=self._to_layout_payload(layout_input),
            reference_snapshots=[self._to_snapshot_reference(snapshot) for snapshot in snapshots],
            user_instructions=payload.user_instructions,
            previous_asset_url=latest_image.asset_url if latest_image and regenerate else None,
        )
        prompt_build = build_scene_image_prompt(scene_request)
        scene = self.repositories.scenes.update_image_prompt(scene_id=scene.id, image_prompt=prompt_build.prompt)
        provider_request = SceneImageGenerationRequestPayload(
            project_id=scene_request.project_id,
            scene_id=scene_request.scene_id,
            scene_title=scene_request.scene_title,
            scene_description=scene_request.scene_description,
            base_image_prompt=scene_request.base_image_prompt,
            character_profile=scene_request.character_profile,
            project_locked_character=scene_request.project_locked_character,
            layout=scene_request.layout,
            reference_snapshots=scene_request.reference_snapshots,
            user_instructions=scene_request.user_instructions,
            prompt_override=prompt_build.prompt,
            previous_asset_url=scene_request.previous_asset_url,
        )
        image_version = len(self.repositories.assets.list_images_for_scene(scene.id)) + 1
        generated = (
            image_provider.edit_image(provider_request)
            if regenerate and latest_image is not None
            else image_provider.generate_image(provider_request)
        )
        revision_note = "scene regeneration" if regenerate else "initial scene generation"
        asset = self.repositories.assets.create_image(
            scene_id=scene.id,
            prompt=generated.revised_prompt or prompt_build.prompt,
            asset_url=generated.asset_url,
            thumbnail_url=generated.thumbnail_url,
            status="ready",
            provider_name=image_provider.provider_name,
            revision_note=revision_note,
        )
        job = self.repositories.jobs.create(
            project_id=project.id,
            job_type="image_generation",
            status="success",
            payload={
                "scene_id": scene.id,
                "character_profile_id": character.id,
                "project_locked_character": project_locked,
                "reference_snapshot_ids": payload.reference_snapshot_ids,
                "mode": "regenerate" if regenerate else "generate",
                "provider_id": provider_id,
                "provider_mode": provider_mode,
            },
            result={"image_asset_id": asset.id},
        )
        self.repositories.jobs.add_log(
            job_id=job.id,
            level="INFO",
            message="장면 이미지가 생성되어 저장되었습니다." if not regenerate else "장면 이미지가 재생성되어 저장되었습니다.",
        )
        self.repositories.revisions.create(
            project_id=project.id,
            entity_type="image_asset",
            entity_id=asset.id,
            version_number=image_version,
            snapshot_json={
                "image_asset_id": asset.id,
                "scene_id": scene.id,
                "scene_title": scene.title,
                "prompt": asset.prompt,
                "provider_id": provider_id,
                "provider_name": image_provider.provider_name,
                "provider_mode": provider_mode,
                "character_profile_id": character.id,
                "character_name": character.name,
                "project_locked_character": project_locked,
                "reference_snapshot_ids": [snapshot.id for snapshot in snapshots],
                "layout": layout_input.model_dump(mode="json"),
                "asset_url": asset.asset_url,
                "thumbnail_url": asset.thumbnail_url,
                "revision_note": revision_note,
                "prompt_metadata": prompt_build.prompt_metadata,
            },
            change_note="단일 장면 이미지 재생성" if regenerate else "장면 이미지 최초 생성",
        )
        self.repositories.session.commit()
        return ImageAssetSummary(
            id=asset.id,
            scene_id=asset.scene_id,
            scene_title=scene.title,
            prompt=asset.prompt,
            asset_url=asset.asset_url,
            thumbnail_url=asset.thumbnail_url,
            status=asset.status,
            provider_id=provider_id,
            provider_name=asset.provider_name,
            provider_mode=provider_mode,
            character_profile_id=character.id,
            character_name=character.name,
            project_locked_character=project_locked,
            reference_snapshot_ids=[snapshot.id for snapshot in snapshots],
            layout=layout_input,
            revision_note=asset.revision_note,
        )

    def _select_image_provider(
        self,
        requested_provider_id: str | None,
        requested_mode: str | None,
    ) -> tuple[str, str, ImageGenerationPort]:
        runtime = RuntimeSettingsResolver(self.repositories)
        provider_id = normalize_provider_id(requested_provider_id, runtime.default_provider("image"))
        provider_mode = normalize_provider_mode(requested_mode, runtime.default_mode("image"))
        return provider_id, provider_mode, build_image_provider(provider_id, provider_mode, runtime)

    def _resolve_scene(self, project_id: str, scene_id: str) -> models.Scene:
        scene = self.repositories.scenes.get(scene_id)
        if scene is None or scene.project_id != project_id:
            raise ValueError(f"Scene not found for project: {scene_id}")
        return scene

    def _resolve_character(
        self,
        project_id: str,
        requested_character_profile_id: str | None,
    ) -> tuple[models.CharacterProfile, bool]:
        locked = self.repositories.characters.get_locked_for_project(project_id)
        if locked is not None:
            return locked, True
        if requested_character_profile_id:
            selected = self.repositories.characters.get(requested_character_profile_id)
            if selected is not None and selected.project_id == project_id:
                return selected, False
        candidates = self.repositories.characters.list_by_project(project_id)
        if not candidates:
            raise ValueError(f"No character profiles found for project: {project_id}")
        return candidates[0], False

    def _resolve_snapshots(self, project_id: str, snapshot_ids: list[str]) -> list[models.Snapshot]:
        return [item for item in self.repositories.snapshots.get_many(snapshot_ids) if item.project_id == project_id]

    def _resolve_layout_input(
        self,
        scene: models.Scene,
        layout: KoreanInfographicLayoutInput | None,
    ) -> KoreanInfographicLayoutInput:
        if layout is not None:
            return KoreanInfographicLayoutInput(
                aspect_ratio=layout.aspect_ratio,
                layout_style=layout.layout_style,
                headline=layout.headline or scene.title,
                subheadline=layout.subheadline or scene.description[:80],
                stat_callouts=list(layout.stat_callouts),
                caption_lines=list(layout.caption_lines),
                color_tokens=list(layout.color_tokens),
            )
        return KoreanInfographicLayoutInput(
            headline=scene.title,
            subheadline=scene.description[:80],
            caption_lines=["한국어 경제 인포그래픽", "세로형 레이아웃"],
        )

    def _to_character_payload(self, character: models.CharacterProfile) -> CharacterProfilePayload:
        return CharacterProfilePayload(
            character_profile_id=character.id,
            name=character.name,
            description=character.description,
            prompt_template=character.prompt_template,
            style_rules=character.style_rules,
            reference_assets=character.reference_assets,
            locked=character.locked,
        )

    def _to_layout_payload(self, layout: KoreanInfographicLayoutInput) -> KoreanInfographicLayoutPayload:
        return KoreanInfographicLayoutPayload(
            aspect_ratio=layout.aspect_ratio,
            layout_style=layout.layout_style,
            headline=layout.headline,
            subheadline=layout.subheadline,
            stat_callouts=[
                InfographicStatCalloutPayload(label=item.label, value=item.value, emphasis=item.emphasis)
                for item in layout.stat_callouts
            ],
            caption_lines=layout.caption_lines,
            color_tokens=layout.color_tokens,
        )

    def _to_snapshot_reference(self, snapshot: models.Snapshot) -> ImageSnapshotReferencePayload:
        return ImageSnapshotReferencePayload(
            snapshot_id=snapshot.id,
            title=snapshot.title,
            image_url=snapshot.image_url,
            source_url=snapshot.source_url,
            note=snapshot.note,
        )


@dataclass(slots=True)
class VideoService:
    repositories: RepositoryRegistry
    providers: ProviderRegistry

    def prepare(self, payload: VideoPrepareRequest) -> list[VideoAssetSummary]:
        project = _resolve_project(self.repositories, payload.project_id)
        provider_id, provider_mode, video_provider = self._select_video_provider(payload.provider_id, payload.provider_mode)
        job = self.repositories.jobs.create(
            project_id=project.id,
            job_type="video_preparation",
            status="running",
            payload={
                "scene_ids": payload.scene_ids,
                "vertical_instructions": payload.vertical_instructions.model_dump(mode="json"),
                "provider_id": provider_id,
                "provider_mode": provider_mode,
            },
            result={},
        )
        created: list[VideoAssetSummary] = []
        for scene_id in payload.scene_ids:
            scene = self._resolve_scene(project.id, scene_id)
            latest_image = self.repositories.assets.latest_image_for_scene(scene.id) if payload.include_latest_image else None
            bundle_path = self._bundle_path(scene.id, len(self.repositories.assets.list_videos_for_scene(scene.id)) + 1)
            request = SceneVideoPreparationRequestPayload(
                project_id=project.id,
                scene_id=scene.id,
                scene_title=scene.title,
                scene_description=scene.description,
                image_asset_id=latest_image.id if latest_image is not None else None,
                image_asset_url=latest_image.asset_url if latest_image is not None else None,
                image_prompt=latest_image.prompt if latest_image is not None else scene.image_prompt,
                motion_prompt=scene.motion_prompt,
                bundle_path=str(bundle_path),
                download_path=str(bundle_path),
                vertical_instructions=self._to_vertical_video_instructions(payload.vertical_instructions),
                user_instructions=payload.user_instructions,
            )
            prompt_build = build_scene_video_prompt(request)
            self._write_video_bundle(
                bundle_path=bundle_path,
                request=request,
                prompt=prompt_build.prompt,
                motion_notes=prompt_build.motion_notes,
            )
            prepared = video_provider.prepare_scene(request)
            asset = self.repositories.assets.create_video(
                scene_id=scene.id,
                prompt=prompt_build.prompt,
                motion_notes=prepared.motion_notes,
                bundle_path=prepared.bundle_path,
                status="ready",
                provider_name=video_provider.provider_name,
            )
            self.repositories.revisions.create(
                project_id=project.id,
                entity_type="video_asset",
                entity_id=asset.id,
                version_number=len(self.repositories.assets.list_videos_for_scene(scene.id)),
                snapshot_json={
                    "video_asset_id": asset.id,
                    "scene_id": scene.id,
                    "scene_title": scene.title,
                    "image_asset_id": latest_image.id if latest_image is not None else None,
                    "prompt": asset.prompt,
                    "motion_notes": asset.motion_notes,
                    "bundle_path": asset.bundle_path,
                    "vertical_instructions": payload.vertical_instructions.model_dump(mode="json"),
                    "provider_id": provider_id,
                    "provider_name": video_provider.provider_name,
                    "provider_mode": provider_mode,
                },
                change_note="장면별 영상 준비 번들 생성",
            )
            self.repositories.jobs.add_log(
                job_id=job.id,
                level="INFO",
                message=f"{scene.title} 장면의 영상 준비 번들이 생성되었습니다.",
            )
            created.append(
                self._video_asset_summary(
                    asset=asset,
                    scene=scene,
                    image_asset=latest_image,
                    vertical_instructions=payload.vertical_instructions,
                    provider_id=provider_id,
                    provider_mode=provider_mode,
                    job_id=job.id,
                )
            )

        job.status = "success"
        job.result = {"count": len(created), "video_asset_ids": [item.id for item in created]}
        self.repositories.session.commit()
        return created

    def execute(self, payload: VideoExecutionRequest) -> list[VideoExecutionSummary]:
        project = _resolve_project(self.repositories, payload.project_id)
        provider_id, provider_mode, video_provider = self._select_video_provider(payload.provider_id, payload.provider_mode)
        job = self.repositories.jobs.create(
            project_id=project.id,
            job_type="video_execution",
            status="running",
            payload={
                "video_asset_ids": payload.video_asset_ids,
                "provider_id": provider_id,
                "provider_mode": provider_mode,
            },
            result={},
        )
        results: list[VideoExecutionSummary] = []
        for asset in self.repositories.assets.get_many_videos(payload.video_asset_ids):
            scene = self._resolve_scene(project.id, asset.scene_id)
            execution = video_provider.execute_bundle(
                VideoExecutionRequestPayload(
                    project_id=project.id,
                    video_asset_id=asset.id,
                    scene_id=scene.id,
                    bundle_path=asset.bundle_path,
                    user_instructions=payload.user_instructions,
                )
            )
            output_path = self._write_mock_execution_receipt(
                execution.output_path,
                {
                    "video_asset_id": asset.id,
                    "scene_id": scene.id,
                    "scene_title": scene.title,
                    "bundle_path": asset.bundle_path,
                    "provider_id": provider_id,
                    "provider_name": video_provider.provider_name,
                    "provider_mode": provider_mode,
                    "provider_job_id": execution.provider_job_id,
                    "status": execution.status,
                },
            )
            self.repositories.revisions.create(
                project_id=project.id,
                entity_type="video_execution",
                entity_id=asset.id,
                version_number=1,
                snapshot_json={
                    "video_asset_id": asset.id,
                    "scene_id": scene.id,
                    "bundle_path": asset.bundle_path,
                    "output_path": output_path,
                    "provider_id": provider_id,
                    "provider_job_id": execution.provider_job_id,
                    "status": execution.status,
                },
                change_note="영상 실행 결과 기록",
            )
            self.repositories.jobs.add_log(
                job_id=job.id,
                level="INFO",
                message=f"{scene.title} 장면의 mock 영상 실행 결과가 기록되었습니다.",
            )
            results.append(
                VideoExecutionSummary(
                    video_asset_id=asset.id,
                    scene_id=scene.id,
                    status=execution.status,
                    provider_id=provider_id,
                    provider_name=video_provider.provider_name,
                    provider_mode=provider_mode,
                    provider_job_id=execution.provider_job_id,
                    output_path=output_path,
                    bundle_path=asset.bundle_path,
                    job_id=job.id,
                )
            )

        job.status = "success"
        job.result = {"count": len(results), "video_asset_ids": [item.video_asset_id for item in results]}
        self.repositories.session.commit()
        return results

    def bundle_path(self, project_id: str, video_asset_id: str) -> str:
        project = _resolve_project(self.repositories, project_id)
        asset = self.repositories.assets.get_video(video_asset_id)
        if asset is None:
            raise ValueError(f"Video asset not found: {video_asset_id}")
        scene = self._resolve_scene(project.id, asset.scene_id)
        _ = scene
        return asset.bundle_path

    def _resolve_scene(self, project_id: str, scene_id: str) -> models.Scene:
        scene = self.repositories.scenes.get(scene_id)
        if scene is None or scene.project_id != project_id:
            raise ValueError(f"Scene not found for project: {scene_id}")
        return scene

    def _bundle_path(self, scene_id: str, version_number: int) -> Path:
        root = Path(get_settings().local_storage_root).expanduser().resolve()
        bundle_dir = root / "video-bundles" / scene_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        return bundle_dir / f"scene-{scene_id}-bundle-v{version_number}.zip"

    def _write_video_bundle(
        self,
        *,
        bundle_path: Path,
        request: SceneVideoPreparationRequestPayload,
        prompt: str,
        motion_notes: str,
    ) -> None:
        manifest = {
            "project_id": request.project_id,
            "scene_id": request.scene_id,
            "scene_title": request.scene_title,
            "scene_description": request.scene_description,
            "image_asset_id": request.image_asset_id,
            "image_asset_url": request.image_asset_url,
            "image_prompt": request.image_prompt,
            "motion_prompt": request.motion_prompt,
            "vertical_instructions": asdict(request.vertical_instructions),
            "user_instructions": request.user_instructions,
        }
        with zipfile.ZipFile(bundle_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.writestr("video_prompt.txt", prompt)
            archive.writestr("motion_notes.txt", motion_notes)
            archive.writestr(
                "README.txt",
                "Mock export bundle containing scene-level video prompt, motion notes, and image references.",
            )
            if request.image_asset_url:
                archive.writestr(
                    "image_reference.json",
                    json.dumps(
                        {
                            "image_asset_id": request.image_asset_id,
                            "image_asset_url": request.image_asset_url,
                            "image_prompt": request.image_prompt,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )

    def _write_mock_execution_receipt(self, output_path: str, payload: dict[str, object]) -> str:
        output_file = Path(output_path).expanduser().resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(output_file)

    def _video_asset_summary(
        self,
        *,
        asset: models.VideoAsset,
        scene: models.Scene,
        image_asset: models.ImageAsset | None,
        vertical_instructions: VerticalVideoInstructionsInput,
        provider_id: str,
        provider_mode: str,
        job_id: str,
    ) -> VideoAssetSummary:
        return VideoAssetSummary(
            id=asset.id,
            scene_id=scene.id,
            scene_title=scene.title,
            image_asset_id=image_asset.id if image_asset is not None else None,
            prompt=asset.prompt,
            motion_notes=asset.motion_notes,
            bundle_path=asset.bundle_path,
            bundle_download_path=f"/api/videos/bundles/{asset.id}?project_id={scene.project_id}",
            status=asset.status,
            provider_id=provider_id,
            provider_name=asset.provider_name,
            provider_mode=provider_mode,
            vertical_instructions=vertical_instructions,
            job_id=job_id,
        )

    def _to_vertical_video_instructions(
        self,
        payload: VerticalVideoInstructionsInput,
        ) -> VerticalVideoInstructionsPayload:
        return VerticalVideoInstructionsPayload(
            aspect_ratio=payload.aspect_ratio,
            duration_seconds=payload.duration_seconds,
            framing=payload.framing,
            caption_style=payload.caption_style,
            pacing=payload.pacing,
            motion_emphasis=payload.motion_emphasis,
        )

    def _select_video_provider(
        self,
        requested_provider_id: str | None,
        requested_mode: str | None,
    ) -> tuple[str, str, VideoWorkflowPort]:
        runtime = RuntimeSettingsResolver(self.repositories)
        provider_id = normalize_provider_id(requested_provider_id, runtime.default_provider("video"))
        provider_mode = normalize_provider_mode(requested_mode, runtime.default_mode("video"))
        return provider_id, provider_mode, build_video_provider(provider_id, provider_mode, runtime)


@dataclass(slots=True)
class JobService:
    repositories: RepositoryRegistry

    def list(self, project_id: str | None = None) -> list[JobSummary]:
        rows = self.repositories.jobs.list_all(project_id)
        return [
            JobSummary(
                id=item.id,
                job_type=item.job_type,
                status=item.status,
                project_id=item.project_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in rows
        ]

    def detail(self, job_id: str) -> JobDetailResponse:
        job = self.repositories.jobs.get(job_id)
        if job is None:
            summaries = self.list()
            return JobDetailResponse(summary=summaries[0], logs=[])
        return JobDetailResponse(
            summary=JobSummary(
                id=job.id,
                job_type=job.job_type,
                status=job.status,
                project_id=job.project_id,
                created_at=job.created_at,
                updated_at=job.updated_at,
            ),
            logs=[JobLogEntry(timestamp=log.timestamp, level=log.level, message=log.message) for log in job.logs],
        )


@dataclass(slots=True)
class ServiceBundle:
    projects: ProjectService
    settings: SettingsService
    issues: IssueService
    statistics: StatisticService
    market: MarketService
    snapshots: SnapshotService
    evidence: EvidenceService
    scripts: ScriptService
    characters: CharacterService
    images: ImageService
    videos: VideoService
    jobs: JobService


def build_service_bundle(session: Session) -> ServiceBundle:
    repositories = RepositoryRegistry(session)
    providers = build_provider_registry(repositories)
    return ServiceBundle(
        projects=ProjectService(repositories),
        settings=SettingsService(repositories),
        issues=IssueService(repositories, providers),
        statistics=StatisticService(repositories, providers),
        market=MarketService(providers),
        snapshots=SnapshotService(repositories, providers),
        evidence=EvidenceService(repositories),
        scripts=ScriptService(repositories, providers),
        characters=CharacterService(repositories),
        images=ImageService(repositories, providers),
        videos=VideoService(repositories, providers),
        jobs=JobService(repositories),
    )
