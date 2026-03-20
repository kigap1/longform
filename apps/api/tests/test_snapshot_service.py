import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.schemas.market import SnapshotCaptureRequest
from app.application.services import ProviderRegistry, SnapshotService
from app.core.config import get_settings
from app.core.database import Base
from app.infrastructure.db.repositories import RepositoryRegistry
from app.infrastructure.providers.adapters import (
    MockImageGeneratorAdapter,
    MockSnapshotAdapter,
    MockVeoWorkflowAdapter,
)
from app.infrastructure.providers.claude_messages import ClaudeMessagesMockAdapter


class SnapshotServiceTests(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        os.environ["STORAGE_MODE"] = "local"
        os.environ["LOCAL_STORAGE_ROOT"] = self.temp_dir.name
        get_settings.cache_clear()

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
            name="스냅샷 엔진 테스트",
            description="Chart / Snapshot Engine 검증",
            issue_focus="환율",
        )
        self.other_project = self.repositories.projects.create(
            name="다른 프로젝트",
            description="프로젝트 링크 필터 확인",
            issue_focus="유가",
        )
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()
        self.temp_dir.cleanup()
        os.environ.pop("STORAGE_MODE", None)
        os.environ.pop("LOCAL_STORAGE_ROOT", None)
        get_settings.cache_clear()

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

    def test_capture_persists_stub_asset_and_attaches_snapshot_evidence(self) -> None:
        service = SnapshotService(self.repositories, self._providers())

        summary = service.capture(
            SnapshotCaptureRequest(
                project_id=self.project.id,
                source_url="https://finance.yahoo.com/quote/KRW=X",
                source_title="Yahoo Finance USD/KRW",
                note="환율 급등 구간",
                attach_as_evidence=True,
                evidence_label="환율 캡처 근거",
            )
        )

        snapshot = self.repositories.snapshots.get(summary.id)
        self.assertIsNotNone(snapshot)
        self.assertEqual(summary.project_id, self.project.id)
        self.assertEqual(summary.source_title, "Yahoo Finance USD/KRW")
        self.assertEqual(summary.capture_mode, "stub")
        self.assertEqual(summary.preview_url, f"/api/snapshot/preview/{summary.id}")
        self.assertTrue(summary.integration_boundary_note)
        self.assertTrue(Path(snapshot.image_url).exists())
        self.assertGreaterEqual(len(summary.attached_evidences), 1)
        self.assertEqual(summary.attached_evidences[0].label, "환율 캡처 근거")

        evidences = self.repositories.evidences.list_by_project(self.project.id)
        self.assertEqual(len(evidences), 1)
        self.assertEqual((evidences[0].metadata_json or {})["snapshot_id"], summary.id)

        jobs = self.repositories.jobs.list_all(self.project.id)
        self.assertEqual(jobs[0].job_type, "snapshot_capture")
        self.assertEqual(jobs[0].status, "success")

    def test_list_filters_by_project_and_keeps_evidence_links(self) -> None:
        service = SnapshotService(self.repositories, self._providers())
        first = service.capture(
            SnapshotCaptureRequest(
                project_id=self.project.id,
                source_url="https://finance.yahoo.com/quote/KRW=X",
                source_title="Yahoo Finance USD/KRW",
                attach_as_evidence=True,
            )
        )
        service.capture(
            SnapshotCaptureRequest(
                project_id=self.other_project.id,
                source_url="https://www.investing.com/commodities/crude-oil",
                source_title="Investing.com WTI",
                attach_as_evidence=True,
            )
        )

        listed = service.list(self.project.id)

        self.assertEqual(len(listed.items), 1)
        self.assertEqual(listed.items[0].id, first.id)
        self.assertEqual(len(listed.items[0].attached_evidences), 1)
