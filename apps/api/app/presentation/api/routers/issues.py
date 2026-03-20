from fastapi import APIRouter, Query

from app.application.schemas.issues import IssueListResponse, IssueRankRequest, IssueRankResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=IssueListResponse)
def list_issues(services: ServiceBundleDep, project_id: str | None = Query(None)) -> IssueListResponse:
    return services.issues.list_ranked(project_id)


@router.post("/rank", response_model=IssueRankResponse)
def rank_issues(payload: IssueRankRequest, services: ServiceBundleDep) -> IssueRankResponse:
    return services.issues.rank(payload)
