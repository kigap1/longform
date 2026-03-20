from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.database import Base, engine
from app.infrastructure.db.repositories import RepositoryRegistry


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo_data(session: Session) -> None:
    repositories = RepositoryRegistry(session)
    project = repositories.projects.first()
    if project is None:
        project = repositories.projects.create(
            name="미국 금리와 원화 변동성",
            description="로컬 실행용 기본 데모 프로젝트",
            issue_focus="금리, 환율, 외국인 자금 흐름",
        )

    if not repositories.settings.list_all():
        repositories.settings.upsert(category="api", key="claude_model", value="claude-sonnet", secret=False)
        repositories.settings.upsert(category="stats", key="freshness_threshold_days", value="45", secret=False)
        repositories.settings.upsert(category="storage", key="mode", value="local", secret=False)

    if not repositories.characters.list_by_project(project.id):
        repositories.characters.create_many(
            project_id=project.id,
            items=[
                {
                    "name": "한결 앵커",
                    "description": "차분하고 신뢰감 있는 경제 전문 진행자",
                    "prompt_template": "한국 경제 전문 진행자, 세로형 인포그래픽 발표",
                    "style_rules": ["네이비 수트", "정면 구도", "깔끔한 스튜디오 조명"],
                    "reference_assets": [],
                    "locked": True,
                },
                {
                    "name": "지안 애널리스트",
                    "description": "도표 중심 설명에 강한 데이터 해설 캐릭터",
                    "prompt_template": "한국어 데이터 해설자, 방송형 앵커 스타일",
                    "style_rules": ["베이지 재킷", "차트 포인팅", "따뜻한 표정"],
                    "reference_assets": [],
                    "locked": False,
                },
            ],
        )

    if not repositories.evidences.list_by_project(project.id):
        repositories.evidences.create_many(
            project_id=project.id,
            items=[
                {
                    "source_kind": "statistic",
                    "label": "ECOS 기준금리",
                    "source_name": "ECOS",
                    "source_url": "https://ecos.bok.or.kr",
                    "indicator_code": "722Y001",
                    "release_date": "2026-03-01",
                    "value": 3.25,
                    "status": "verified",
                    "note": "데모용 공식 통계 근거",
                },
                {
                    "source_kind": "market_data",
                    "label": "Yahoo Finance USD/KRW",
                    "source_name": "Yahoo Finance",
                    "source_url": "https://finance.yahoo.com",
                    "release_date": "2026-03-20",
                    "value": 1372.5,
                    "status": "verified",
                    "note": "보조 시장 근거",
                },
            ],
        )

    if not repositories.jobs.list_all(project.id):
        job = repositories.jobs.create(
            project_id=project.id,
            job_type="script_generation",
            status="success",
            payload={"issue": "미국 금리와 원화 변동성"},
            result={"script_id": "demo-script"},
        )
        repositories.jobs.add_log(job_id=job.id, level="INFO", message="데모 작업이 생성되었습니다.")

    session.commit()

