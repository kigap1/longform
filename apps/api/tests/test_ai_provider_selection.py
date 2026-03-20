from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.schemas.assets import ImageGenerateRequest, VideoExecutionRequest, VideoPrepareRequest
from app.application.schemas.platform import AppSettingUpsertRequest
from app.application.schemas.scripts import ScriptGenerationRequest
from app.application.services import ImageService, ProviderRegistry, ScriptService, SettingsService, VideoService
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
from app.infrastructure.providers.claude_messages import ClaudeMessagesMockAdapter


class AIProviderSelectionTests(TestCase):
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
            name="AI provider 테스트",
            description="OpenAI/Claude/Gemini 선택 검증",
            issue_focus="환율",
        )
        self.issue = models.Issue(
            project_id=self.project.id,
            title="원화 변동성",
            category="economy",
            summary="환율과 금리 이슈",
            priority_score=0.8,
            ranking_reasons=["테스트"],
        )
        self.scene = models.Scene(
            project_id=self.project.id,
            title="오프닝",
            description="환율 장면",
            image_prompt="앵커와 차트",
            motion_prompt="줌 인",
            order_index=1,
        )
        self.character = models.CharacterProfile(
            project_id=self.project.id,
            name="한결 앵커",
            description="기본 앵커",
            prompt_template="경제 뉴스 앵커",
            style_rules=["정면"],
            reference_assets=[],
            locked=True,
        )
        self.session.add_all([self.issue, self.scene, self.character])
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _providers(self) -> ProviderRegistry:
        return ProviderRegistry(
            news=[],
            statistics=[EcosAdapter(), KosisAdapter(), FredAdapter(), OecdAdapter()],
            market_data=[YahooFinanceAdapter(), InvestingAdapter(), SeekingAlphaAdapter()],
            snapshot=MockSnapshotAdapter(),
            script_model=ClaudeMessagesMockAdapter(),
            image_generator=MockImageGeneratorAdapter(),
            video_workflow=MockVeoWorkflowAdapter(),
        )

    def test_ai_provider_catalog_keeps_openai_claude_gemini_order(self) -> None:
        settings_service = SettingsService(self.repositories)
        settings_service.upsert(AppSettingUpsertRequest(category="api", key="script_default_provider", value="openai"))
        catalog = settings_service.ai_provider_catalog()

        self.assertEqual([item.id for item in catalog.items][:3], ["openai", "claude", "gemini"])
        self.assertEqual(catalog.items[-1].id, "kling")
        self.assertEqual(catalog.defaults["script"], "openai")
        claude_image = next(item for item in catalog.items if item.id == "claude").stages[1]
        self.assertFalse(claude_image.supported)
        kling_video = next(item for item in catalog.items if item.id == "kling").stages[2]
        self.assertTrue(kling_video.supported)

    def test_gemini_mock_selection_flows_through_script_image_and_video_services(self) -> None:
        script_service = ScriptService(self.repositories, self._providers())
        image_service = ImageService(self.repositories, self._providers())
        video_service = VideoService(self.repositories, self._providers())

        script = script_service.generate(
            ScriptGenerationRequest(
                project_id=self.project.id,
                issue_id=self.issue.id,
                provider_id="gemini",
                provider_mode="mock",
            )
        )
        image = image_service.generate(
            ImageGenerateRequest(
                project_id=self.project.id,
                scene_id=self.scene.id,
                provider_id="gemini",
                provider_mode="mock",
            )
        )
        videos = video_service.prepare(
            VideoPrepareRequest(
                project_id=self.project.id,
                scene_ids=[self.scene.id],
                provider_id="gemini",
                provider_mode="mock",
            )
        )

        self.assertEqual(script.provider_id, "gemini")
        self.assertEqual(script.provider_name, "Gemini")
        self.assertEqual(image.provider_id, "gemini")
        self.assertEqual(image.provider_name, "Gemini")
        self.assertEqual(videos[0].provider_id, "gemini")
        self.assertEqual(videos[0].provider_name, "Gemini")

    def test_kling_mock_selection_flows_through_video_service(self) -> None:
        video_service = VideoService(self.repositories, self._providers())

        videos = video_service.prepare(
            VideoPrepareRequest(
                project_id=self.project.id,
                scene_ids=[self.scene.id],
                provider_id="kling",
                provider_mode="mock",
            )
        )

        self.assertEqual(videos[0].provider_id, "kling")
        self.assertEqual(videos[0].provider_name, "Kling AI")

    def test_kling_real_bridge_can_submit_execution_job(self) -> None:
        class _KlingBridgeHandler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{\"job_id\":\"kling-job-1\",\"status\":\"queued\",\"output_path\":\"/tmp/kling.mp4\"}')

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                _ = (format, args)

        server = HTTPServer(("127.0.0.1", 0), _KlingBridgeHandler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            self.repositories.settings.upsert(category="api", key="kling_api_key", value="test-key", secret=True)
            self.repositories.settings.upsert(
                category="api",
                key="kling_base_url",
                value=f"http://127.0.0.1:{server.server_port}",
                secret=False,
            )
            self.repositories.settings.upsert(category="api", key="kling_submit_path", value="/bridge/submit", secret=False)
            self.session.commit()

            video_service = VideoService(self.repositories, self._providers())
            prepared = video_service.prepare(
                VideoPrepareRequest(
                    project_id=self.project.id,
                    scene_ids=[self.scene.id],
                    provider_id="kling",
                    provider_mode="real",
                )
            )
            executed = video_service.execute(
                VideoExecutionRequest(
                    project_id=self.project.id,
                    video_asset_ids=[prepared[0].id],
                    provider_id="kling",
                    provider_mode="real",
                )
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

        self.assertEqual(prepared[0].provider_id, "kling")
        self.assertEqual(executed[0].provider_id, "kling")
        self.assertEqual(executed[0].provider_job_id, "kling-job-1")
        self.assertEqual(executed[0].status, "queued")

    def test_claude_image_selection_is_rejected_with_clear_boundary_error(self) -> None:
        service = ImageService(self.repositories, self._providers())

        with self.assertRaises(NotImplementedError):
            service.generate(
                ImageGenerateRequest(
                    project_id=self.project.id,
                    scene_id=self.scene.id,
                    provider_id="claude",
                    provider_mode="mock",
                )
            )
