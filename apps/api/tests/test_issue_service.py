from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.schemas.issues import IssueRankRequest
from app.application.services import IssueService, ProviderRegistry
from app.core.database import Base
from app.infrastructure.db.repositories import RepositoryRegistry
from app.infrastructure.providers.adapters import (
    MockGlobalNewsAdapter,
    MockImageGeneratorAdapter,
    MockKoreanNewsAdapter,
    MockSnapshotAdapter,
    MockVeoWorkflowAdapter,
)
from app.infrastructure.providers.claude_messages import ClaudeMessagesMockAdapter


class IssueServiceTests(TestCase):
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
            name="이슈 서비스 테스트",
            description="뉴스 랭킹 저장 검증",
            issue_focus="금리",
        )
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_rank_persists_articles_with_json_safe_payloads(self) -> None:
        service = IssueService(
            self.repositories,
            ProviderRegistry(
                news=[MockKoreanNewsAdapter(), MockGlobalNewsAdapter()],
                statistics=[],
                market_data=[],
                snapshot=MockSnapshotAdapter(),
                script_model=ClaudeMessagesMockAdapter(),
                image_generator=MockImageGeneratorAdapter(),
                video_workflow=MockVeoWorkflowAdapter(),
            ),
        )

        ranked = service.rank(IssueRankRequest(project_id=self.project.id, keywords=["금리", "환율"]))

        self.assertGreaterEqual(len(ranked.items), 1)
        persisted = self.repositories.issues.list_by_project(self.project.id)
        self.assertGreaterEqual(len(persisted), 1)
        self.assertTrue(all(isinstance(article.raw_payload.get("published_at"), str) for issue in persisted for article in issue.articles))
