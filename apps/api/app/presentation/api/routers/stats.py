from fastapi import APIRouter, Query

from app.application.schemas.stats import (
    EvidenceContextRequest,
    EvidenceContextResponse,
    FactCheckRequest,
    FactCheckResponse,
    RecommendStatisticRequest,
    SearchStatisticRequest,
    StatisticListResponse,
    StatisticSeriesResponse,
)
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/recommend", response_model=StatisticListResponse)
def recommend_stats(payload: RecommendStatisticRequest, services: ServiceBundleDep) -> StatisticListResponse:
    return services.statistics.recommend(payload)


@router.post("/search", response_model=StatisticListResponse)
def search_stats(payload: SearchStatisticRequest, services: ServiceBundleDep) -> StatisticListResponse:
    return services.statistics.search(payload)


@router.get("/series", response_model=StatisticSeriesResponse)
def get_stat_series(services: ServiceBundleDep, indicator_code: str = Query(...)) -> StatisticSeriesResponse:
    return services.statistics.series(indicator_code)


@router.post("/evidence-context", response_model=EvidenceContextResponse)
def build_evidence_context(payload: EvidenceContextRequest, services: ServiceBundleDep) -> EvidenceContextResponse:
    return services.statistics.evidence_context(payload)


@router.post("/fact-check", response_model=FactCheckResponse)
def fact_check_stats(payload: FactCheckRequest, services: ServiceBundleDep) -> FactCheckResponse:
    return services.statistics.fact_check(payload)
