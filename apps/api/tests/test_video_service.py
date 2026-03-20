import json
import shutil
import zipfile
from pathlib import Path
from unittest import TestCase

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.application.schemas.assets import VideoExecutionRequest, VideoPrepareRequest, VerticalVideoInstructionsInput
from app.application.services import ProviderRegistry, VideoService
from app.core.database import Base
from app.infrastructure.db import models
from app.infrastructure.db.repositories import RepositoryRegistry
from app.infrastructure.providers.adapters import (
    MockImageGeneratorAdapter,
    MockSnapshotAdapter,
    MockVeoWorkflowAdapter,
)
from app.infrastructure.providers.claude_messages import ClaudeMessagesMockAdapter


class VideoServiceTests(TestCase):
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
            name="비디오 엔진 테스트",
            description="Video Generation Preparation Engine 검증",
            issue_focus="환율",
        )
        self.scene = models.Scene(
            project_id=self.project.id,
            title="환율 오프닝",
            description="환율 상승과 시장 반응을 설명하는 첫 장면",
            image_prompt="앵커와 환율 차트가 함께 보이는 세로형 장면",
            motion_prompt="차트 줌 인",
            order_index=1,
        )
        self.session.add(self.scene)
        self.session.flush()
        self.image_asset = models.ImageAsset(
            scene_id=self.scene.id,
            prompt="한국어 인포그래픽, 환율 차트, 앵커 유지",
            asset_url="https://example.com/mock-image.png",
            thumbnail_url="https://example.com/mock-thumb.png",
            status="ready",
            provider_name="Mock Image Generator",
            revision_note="seed image",
        )
        self.session.add(self.image_asset)
        self.session.commit()
        self.storage_root = Path("storage").resolve()

    def tearDown(self) -> None:
        if self.storage_root.exists():
            shutil.rmtree(self.storage_root)
        self.session.close()
        self.engine.dispose()

    def _providers(self) -> ProviderRegistry:
        return ProviderRegistry(
            news=[],
            statistics=[],
            market_data=[],
            snapshot=MockSnapshotAdapter(),
            script_model=ClaudeMessagesMockAdapter(),
            image_generator=MockImageGeneratorAdapter(),
            video_workflow=MockVeoWorkflowAdapter(),
        )

    def test_prepare_creates_scene_level_bundle_with_image_and_prompts(self) -> None:
        service = VideoService(self.repositories, self._providers())
        results = service.prepare(
            VideoPrepareRequest(
                project_id=self.project.id,
                scene_ids=[self.scene.id],
                vertical_instructions=VerticalVideoInstructionsInput(
                    aspect_ratio="9:16",
                    duration_seconds=10,
                    framing="중앙 인물과 자막 안전영역",
                    caption_style="굵은 한국어 자막",
                    pacing="fast",
                    motion_emphasis="high",
                ),
                user_instructions="첫 1초에 핵심 숫자를 보여줘",
            )
        )

        self.assertEqual(len(results), 1)
        summary = results[0]
        self.assertEqual(summary.scene_title, "환율 오프닝")
        self.assertEqual(summary.image_asset_id, self.image_asset.id)
        self.assertEqual(summary.provider_mode, "mock")
        self.assertTrue(Path(summary.bundle_path).exists())
        self.assertIn(f"project_id={self.project.id}", summary.bundle_download_path)

        with zipfile.ZipFile(summary.bundle_path) as archive:
            names = set(archive.namelist())
            self.assertIn("manifest.json", names)
            self.assertIn("video_prompt.txt", names)
            self.assertIn("motion_notes.txt", names)
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            self.assertEqual(manifest["scene_id"], self.scene.id)
            self.assertEqual(manifest["image_asset_id"], self.image_asset.id)
            self.assertEqual(manifest["vertical_instructions"]["aspect_ratio"], "9:16")

        jobs = self.repositories.jobs.list_all(self.project.id)
        self.assertEqual(jobs[0].job_type, "video_preparation")

    def test_execute_writes_mock_execution_receipt_and_job(self) -> None:
        service = VideoService(self.repositories, self._providers())
        prepared = service.prepare(
            VideoPrepareRequest(
                project_id=self.project.id,
                scene_ids=[self.scene.id],
            )
        )[0]

        executions = service.execute(
            VideoExecutionRequest(
                project_id=self.project.id,
                video_asset_ids=[prepared.id],
                user_instructions="mock 실행",
            )
        )

        self.assertEqual(len(executions), 1)
        execution = executions[0]
        self.assertEqual(execution.status, "success")
        self.assertTrue(Path(execution.output_path).exists())
        payload = json.loads(Path(execution.output_path).read_text(encoding="utf-8"))
        self.assertEqual(payload["video_asset_id"], prepared.id)

        revisions = list(
            self.session.scalars(
                select(models.ProjectRevision)
                .where(models.ProjectRevision.project_id == self.project.id)
                .order_by(models.ProjectRevision.created_at.asc())
            )
        )
        self.assertGreaterEqual(len(revisions), 2)
        self.assertEqual(revisions[-1].entity_type, "video_execution")
