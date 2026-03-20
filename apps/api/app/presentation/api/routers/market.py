from fastapi import APIRouter, Query

from app.application.schemas.market import MarketSearchRequest, MarketSearchResponse, MarketSeriesResponse
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/search", response_model=MarketSearchResponse)
def search_market(payload: MarketSearchRequest, services: ServiceBundleDep) -> MarketSearchResponse:
    return services.market.search(payload)


@router.get("/series", response_model=MarketSeriesResponse)
def market_series(services: ServiceBundleDep, symbol: str = Query(...)) -> MarketSeriesResponse:
    return services.market.series(symbol)
