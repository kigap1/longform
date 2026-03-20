from tempfile import TemporaryDirectory
from unittest import TestCase
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.schemas.market import MarketSearchRequest, SnapshotCaptureRequest
from app.application.schemas.stats import RecommendStatisticRequest
from app.application.services import build_service_bundle
from app.core.config import get_settings
from app.core.database import Base
from app.infrastructure.db.repositories import RepositoryRegistry


class ServiceBundleSmokeTests(TestCase):
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
            name="서비스 번들 스모크 테스트",
            description="Phase 9 smoke",
            issue_focus="금리와 환율",
        )
        self.repositories.characters.create_many(
            project_id=self.project.id,
            items=[
                {
                    "name": "한결 앵커",
                    "description": "테스트 기본 캐릭터",
                    "prompt_template": "한국 경제 전문 진행자",
                    "style_rules": ["네이비 수트"],
                    "reference_assets": [],
                    "locked": True,
                }
            ],
        )
        self.session.commit()
        self.services = build_service_bundle(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()
        self.temp_dir.cleanup()
        os.environ.pop("STORAGE_MODE", None)
        os.environ.pop("LOCAL_STORAGE_ROOT", None)
        get_settings.cache_clear()

    def test_core_services_return_connected_outputs(self) -> None:
        projects = self.services.projects.list()
        issues = self.services.issues.list_ranked(self.project.id)
        issue_id = issues.items[0].id

        statistics = self.services.statistics.recommend(
            RecommendStatisticRequest(project_id=self.project.id, issue_id=issue_id)
        )
        market = self.services.market.search(MarketSearchRequest(query="KRW"))
        snapshots = self.services.snapshots.capture(
            SnapshotCaptureRequest(
                project_id=self.project.id,
                source_url="https://finance.yahoo.com/quote/KRW=X",
                source_title="Yahoo Finance USD/KRW",
                attach_as_evidence=True,
            )
        )
        characters = self.services.characters.list(self.project.id)
        jobs = self.services.jobs.list(self.project.id)

        self.assertGreaterEqual(len(projects.items), 1)
        self.assertGreaterEqual(len(issues.items), 1)
        self.assertGreaterEqual(len(statistics.items), 1)
        self.assertGreaterEqual(len(market.items), 1)
        self.assertTrue(snapshots.preview_url.endswith(snapshots.id))
        self.assertGreaterEqual(len(characters.items), 1)
        self.assertGreaterEqual(len(jobs), 1)
