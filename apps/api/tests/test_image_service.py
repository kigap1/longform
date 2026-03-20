from unittest import TestCase

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.application.schemas.assets import (
    ImageGenerateRequest,
    ImageRegenerateSceneRequest,
    KoreanInfographicLayoutInput,
    SceneImagePromptUpdateRequest,
)
from app.application.services import ImageService, ProviderRegistry
from app.core.database import Base
from app.infrastructure.db import models
from app.infrastructure.db.repositories import RepositoryRegistry
from app.infrastructure.providers.adapters import (
    MockImageGeneratorAdapter,
    MockSnapshotAdapter,
    MockVeoWorkflowAdapter,
)
from app.infrastructure.providers.claude_messages import ClaudeMessagesMockAdapter


class ImageServiceTests(TestCase):
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
            name="이미지 엔진 테스트",
            description="캐릭터 일관성 및 이미지 파이프라인 검증",
            issue_focus="환율",
        )
        self.scene = models.Scene(
            project_id=self.project.id,
            title="환율 오프닝",
            description="환율 상승과 시장 반응을 설명하는 첫 장면",
            image_prompt="앵커가 환율 차트를 가리키는 기본 장면",
            motion_prompt="카메라 줌 인",
            order_index=1,
        )
        self.locked_character = models.CharacterProfile(
            project_id=self.project.id,
            name="한결 앵커",
            description="프로젝트 기본 앵커",
            prompt_template="한국 경제 뉴스 앵커, 세로형 인포그래픽",
            style_rules=["네이비 수트", "정면 구도"],
            reference_assets=["char-anchor-v1.png"],
            locked=True,
        )
        self.optional_character = models.CharacterProfile(
            project_id=self.project.id,
            name="지안 애널리스트",
            description="대체 해설 캐릭터",
            prompt_template="차트 설명 중심 데이터 해설자",
            style_rules=["베이지 재킷"],
            reference_assets=[],
            locked=False,
        )
        self.snapshot = models.Snapshot(
            project_id=self.project.id,
            title="USD/KRW 캡처",
            source_url="https://example.com/chart",
            image_url="https://example.com/chart.png",
            note="차트 구도 참고",
            captured_at="2026-03-20T09:00:00+00:00",
        )
        self.session.add_all([self.scene, self.locked_character, self.optional_character, self.snapshot])
        self.session.commit()

    def tearDown(self) -> None:
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

    def test_generate_respects_project_locked_character_and_persists_asset(self) -> None:
        service = ImageService(self.repositories, self._providers())
        summary = service.generate(
            ImageGenerateRequest(
                project_id=self.project.id,
                scene_id=self.scene.id,
                character_profile_id=self.optional_character.id,
                reference_snapshot_ids=[self.snapshot.id],
                layout=KoreanInfographicLayoutInput(
                    headline="원/달러 환율 점검",
                    subheadline="장중 환율 흐름",
                ),
                user_instructions="한국어 자막을 크게 넣어줘",
            )
        )

        self.assertEqual(summary.character_profile_id, self.locked_character.id)
        self.assertTrue(summary.project_locked_character)
        self.assertEqual(summary.reference_snapshot_ids, [self.snapshot.id])
        self.assertEqual(summary.provider_id, "openai")
        self.assertEqual(summary.provider_name, "OpenAI")
        self.assertEqual(summary.scene_title, "환율 오프닝")
        self.assertIn("USD/KRW 캡처", summary.prompt)

        persisted_scene = self.repositories.scenes.get(self.scene.id)
        self.assertIsNotNone(persisted_scene)
        self.assertEqual(persisted_scene.image_prompt, summary.prompt)
        self.assertEqual(len(self.repositories.assets.list_images_for_scene(self.scene.id)), 1)

    def test_update_scene_prompt_and_regenerate_single_scene(self) -> None:
        service = ImageService(self.repositories, self._providers())
        generated = service.generate(
            ImageGenerateRequest(
                project_id=self.project.id,
                scene_id=self.scene.id,
                reference_snapshot_ids=[self.snapshot.id],
            )
        )
        updated_prompt = service.update_scene_prompt(
            SceneImagePromptUpdateRequest(
                project_id=self.project.id,
                scene_id=self.scene.id,
                prompt="한국어 인포그래픽, 큰 숫자, 환율 차트, 동일 캐릭터 유지",
            )
        )
        regenerated = service.regenerate_scene(
            ImageRegenerateSceneRequest(
                project_id=self.project.id,
                scene_id=self.scene.id,
                reference_snapshot_ids=[self.snapshot.id],
                prompt_override=updated_prompt.image_prompt,
                user_instructions="기존 장면을 유지하면서 숫자만 더 강조",
            )
        )

        self.assertEqual(generated.scene_id, regenerated.scene_id)
        self.assertEqual(regenerated.revision_note, "scene regeneration")
        self.assertEqual(len(self.repositories.assets.list_images_for_scene(self.scene.id)), 2)

        revisions = list(
            self.session.scalars(
                select(models.ProjectRevision)
                .where(models.ProjectRevision.project_id == self.project.id)
                .order_by(models.ProjectRevision.created_at.asc())
            )
        )
        self.assertEqual(len(revisions), 3)
        self.assertEqual(revisions[-1].entity_type, "image_asset")
        self.assertEqual(revisions[-1].snapshot_json["revision_note"], "scene regeneration")
