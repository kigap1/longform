from unittest import TestCase

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.application.schemas.scripts import RegenerateSectionRequest, ScriptGenerationRequest
from app.application.services import ProviderRegistry, ScriptService
from app.core.database import Base
from app.infrastructure.db import models
from app.infrastructure.db.repositories import RepositoryRegistry
from app.infrastructure.providers.adapters import (
    EcosAdapter,
    FredAdapter,
    InvestingAdapter,
    KosisAdapter,
    MockImageGeneratorAdapter,
    MockSnapshotAdapter,
    MockVeoWorkflowAdapter,
    OecdAdapter,
    SeekingAlphaAdapter,
    YahooFinanceAdapter,
)
from app.infrastructure.providers.claude_messages import ClaudeMessagesAPIAdapter, ClaudeMessagesMockAdapter


class ScriptServiceTests(TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", future=True)
        self.Session = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        Base.metadata.create_all(bind=self.engine)
        self.session = self.Session()
        self.repositories = RepositoryRegistry(self.session)
        self.project = self.repositories.projects.create(
            name="스크립트 엔진 테스트",
            description="Claude Script Generation Engine 검증용",
            issue_focus="금리와 환율",
        )
        self.issue = models.Issue(
            project_id=self.project.id,
            title="미국 금리와 원화 변동성",
            category="economy",
            summary="금리 변화가 원화와 국내 위험자산에 미치는 영향을 설명합니다.",
            priority_score=0.9,
            ranking_reasons=["테스트 이슈"],
        )
        self.session.add(self.issue)
        self.session.flush()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _providers(self, script_model) -> ProviderRegistry:
        return ProviderRegistry(
            news=[],
            statistics=[EcosAdapter(), KosisAdapter(), FredAdapter(), OecdAdapter()],
            market_data=[YahooFinanceAdapter(), InvestingAdapter(), SeekingAlphaAdapter()],
            snapshot=MockSnapshotAdapter(),
            script_model=script_model,
            image_generator=MockImageGeneratorAdapter(),
            video_workflow=MockVeoWorkflowAdapter(),
        )

    def test_generate_supports_request_level_mock_override(self) -> None:
        service = ScriptService(
            self.repositories,
            self._providers(
                ClaudeMessagesAPIAdapter(
                    api_key=None,
                    api_url="https://api.anthropic.com/v1/messages",
                    api_version="2023-06-01",
                    model_name="claude-sonnet-test",
                )
            ),
        )

        summary = service.generate(
            ScriptGenerationRequest(
                project_id=self.project.id,
                issue_id=self.issue.id,
                indicator_codes=["722Y001", "FEDFUNDS"],
                market_symbols=["KRW=X"],
                user_instructions="숫자 설명을 쉽게 풀어줘",
                provider_mode="mock",
                style_preset="설명형",
                tone="차분한 분석형",
                audience_type="대중",
            )
        )

        self.assertEqual(summary.provider_mode, "mock")
        self.assertEqual(summary.provider_id, "openai")
        self.assertEqual(summary.provider_name, "OpenAI")
        self.assertGreaterEqual(len(summary.sections), 3)
        self.assertGreaterEqual(len(summary.scenes), 2)
        self.assertGreaterEqual(len(summary.evidence_mappings), 1)
        self.assertTrue(any(scene.evidence_ids for scene in summary.scenes))

        script = self.repositories.scripts.get(summary.id)
        self.assertIsNotNone(script)
        self.assertEqual((script.prompt_snapshot or {})["provider"]["mode"], "mock")
        self.assertEqual((script.prompt_snapshot or {})["provider"]["id"], "openai")
        self.assertGreaterEqual(len((script.prompt_snapshot or {})["result"]["sections"]), 3)
        self.assertGreaterEqual(len((script.prompt_snapshot or {})["result"]["scenes"]), 2)

    def test_regenerate_section_increments_version_and_stores_full_revision_snapshot(self) -> None:
        service = ScriptService(self.repositories, self._providers(ClaudeMessagesMockAdapter()))
        summary = service.generate(
            ScriptGenerationRequest(
                project_id=self.project.id,
                issue_id=self.issue.id,
                indicator_codes=["722Y001"],
                market_symbols=["KRW=X"],
                user_instructions="기본 초안 생성",
            )
        )

        regenerated = service.regenerate_section(
            RegenerateSectionRequest(
                project_id=self.project.id,
                script_id=summary.id,
                section_id=summary.sections[1].id,
                user_instructions="통계를 더 쉽게 설명해줘",
                provider_mode="mock",
            )
        )

        script = self.repositories.scripts.get(summary.id)
        self.assertIsNotNone(script)
        self.assertEqual(regenerated.version_number, 2)
        self.assertEqual(script.version_number, 2)
        self.assertIn("재생성", regenerated.section.content)
        self.assertEqual((script.prompt_snapshot or {})["provider"]["mode"], "mock")
        self.assertGreaterEqual(len((script.prompt_snapshot or {})["result"]["sections"]), 3)
        self.assertGreaterEqual(len((script.prompt_snapshot or {})["result"]["evidence_mappings"]), 1)

        revisions = list(
            self.session.scalars(
                select(models.ProjectRevision)
                .where(models.ProjectRevision.entity_id == summary.id)
                .order_by(models.ProjectRevision.version_number.asc())
            )
        )
        self.assertEqual(len(revisions), 2)
        self.assertEqual(revisions[-1].version_number, 2)
        self.assertEqual(revisions[-1].snapshot_json["version_number"], 2)
        self.assertGreaterEqual(len(revisions[-1].snapshot_json["sections"]), 3)
        self.assertGreaterEqual(len(revisions[-1].snapshot_json["scenes"]), 2)
