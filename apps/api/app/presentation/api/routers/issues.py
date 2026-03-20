from fastapi import APIRouter, Query

from app.application.schemas.issues import IssueListResponse, IssueRankRequest, IssueRankResponse
from app.presentation.api.errors import raise_service_http_error
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.get("", response_model=IssueListResponse)
def list_issues(services: ServiceBundleDep, project_id: str | None = Query(None)) -> IssueListResponse:
    return services.issues.list_ranked(project_id)


@router.post("/rank", response_model=IssueRankResponse)
def rank_issues(payload: IssueRankRequest, services: ServiceBundleDep) -> IssueRankResponse:
    try:
        return services.issues.rank(payload)
    except Exception as exc:
        raise_service_http_error(exc)
