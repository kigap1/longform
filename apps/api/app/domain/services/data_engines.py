from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence

from app.domain.provider_interfaces import (
    IndicatorPayload,
    MarketDataProviderPort,
    MarketQuotePayload,
    StatisticsProviderPort,
    TimeSeriesPointPayload,
)


@dataclass(slots=True, frozen=True)
class EvidenceContextLine:
    source_kind: str
    label: str
    context_line: str
    source_name: str
    source_url: str
    indicator_code: str | None = None
    release_date: str | None = None
    value: float | None = None
    stale: bool = False


def _parse_release_date(value: str) -> date:
    return date.fromisoformat(value)


def _normalize(value: str) -> str:
    return value.strip().lower()


@dataclass(slots=True)
class StatisticsVerificationEngine:
    providers: Sequence[StatisticsProviderPort]

    def detect_stale(
        self,
        release_date: str,
        *,
        freshness_threshold_days: int,
        today: date | None = None,
    ) -> bool:
        reference_day = today or date.today()
        return (reference_day - _parse_release_date(release_date)).days > freshness_threshold_days

    def recommend_indicators(self, issue_title: str, *, max_items: int = 8) -> list[IndicatorPayload]:
        rows: list[IndicatorPayload] = []
        for provider in self.providers:
            rows.extend(provider.recommend_indicators(issue_title))
        return self._limit_unique(rows, max_items=max_items)

    def search_indicators(
        self,
        keyword: str,
        *,
        source_scope: Sequence[str] | None = None,
        max_items: int = 12,
    ) -> list[IndicatorPayload]:
        allowed_sources = {_normalize(item) for item in source_scope or []}
        rows: list[IndicatorPayload] = []
        for provider in self.providers:
            if allowed_sources and _normalize(provider.provider_name) not in allowed_sources:
                continue
            rows.extend(provider.search_indicators(keyword))
        return self._limit_unique(rows, max_items=max_items)

    def get_indicator(self, indicator_code: str, *, preferred_source: str | None = None) -> IndicatorPayload | None:
        providers = self._ordered_providers(preferred_source)
        for provider in providers:
            item = provider.get_indicator(indicator_code)
            if item is not None:
                return item
        return None

    def get_time_series(
        self,
        indicator_code: str,
        *,
        preferred_source: str | None = None,
    ) -> tuple[IndicatorPayload, list[TimeSeriesPointPayload]] | None:
        indicator = self.get_indicator(indicator_code, preferred_source=preferred_source)
        if indicator is None:
            return None
        return indicator, list(indicator.series_points)

    def build_evidence_context(
        self,
        *,
        indicators: Sequence[IndicatorPayload],
        market_assets: Sequence[MarketQuotePayload] = (),
        freshness_threshold_days: int = 45,
        today: date | None = None,
    ) -> tuple[list[EvidenceContextLine], str]:
        context_items: list[EvidenceContextLine] = []
        for indicator in indicators:
            stale = self.detect_stale(
                indicator.release_date,
                freshness_threshold_days=freshness_threshold_days,
                today=today,
            )
            freshness_label = "주의: 오래된 값" if stale else "최신값"
            context_items.append(
                EvidenceContextLine(
                    source_kind="statistic",
                    label=f"{indicator.source_name} {indicator.name}",
                    indicator_code=indicator.code,
                    release_date=indicator.release_date,
                    value=indicator.latest_value,
                    stale=stale,
                    source_name=indicator.source_name,
                    source_url=indicator.source_url,
                    context_line=(
                        f"[공식 통계] {indicator.source_name} {indicator.name}({indicator.code}) = "
                        f"{indicator.latest_value}{indicator.unit}, 발표일 {indicator.release_date}, {freshness_label}. "
                        f"{indicator.description}"
                    ),
                )
            )

        for asset in market_assets:
            context_items.append(
                EvidenceContextLine(
                    source_kind="market_data",
                    label=f"{asset.source_name} {asset.display_name}",
                    indicator_code=asset.symbol,
                    release_date=asset.as_of,
                    value=asset.latest_value,
                    stale=False,
                    source_name=asset.source_name,
                    source_url=asset.source_url,
                    context_line=(
                        f"[보조 시장자료] {asset.source_name} {asset.display_name}({asset.symbol}) = "
                        f"{asset.latest_value} {asset.currency}, 변동률 {asset.change_percent}%. {asset.note}"
                    ),
                )
            )

        combined_context = "\n".join(item.context_line for item in context_items)
        return context_items, combined_context

    def _limit_unique(self, rows: Sequence[IndicatorPayload], *, max_items: int) -> list[IndicatorPayload]:
        unique: list[IndicatorPayload] = []
        seen: set[tuple[str, str]] = set()
        for item in rows:
            key = (_normalize(item.source_name), _normalize(item.code))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
            if len(unique) >= max_items:
                break
        return unique

    def _ordered_providers(self, preferred_source: str | None) -> list[StatisticsProviderPort]:
        if preferred_source is None:
            return list(self.providers)
        preferred = []
        others = []
        normalized = _normalize(preferred_source)
        for provider in self.providers:
            if _normalize(provider.provider_name) == normalized:
                preferred.append(provider)
            else:
                others.append(provider)
        return preferred + others


@dataclass(slots=True)
class MarketDataEngine:
    providers: Sequence[MarketDataProviderPort]

    def search_assets(
        self,
        query: str,
        *,
        asset_class: str | None = None,
        source_scope: Sequence[str] | None = None,
        max_items: int = 12,
    ) -> list[MarketQuotePayload]:
        allowed_sources = {_normalize(item) for item in source_scope or []}
        rows: list[MarketQuotePayload] = []
        for provider in self.providers:
            if allowed_sources and _normalize(provider.provider_name) not in allowed_sources:
                continue
            rows.extend(provider.search_assets(query, asset_class))
        return self._limit_unique(rows, max_items=max_items)

    def get_asset(self, symbol: str, *, preferred_source: str | None = None) -> MarketQuotePayload | None:
        providers = self._ordered_providers(preferred_source)
        for provider in providers:
            item = provider.get_asset(symbol)
            if item is not None:
                return item
        return None

    def get_time_series(
        self,
        symbol: str,
        *,
        preferred_source: str | None = None,
    ) -> tuple[MarketQuotePayload, list[TimeSeriesPointPayload]] | None:
        asset = self.get_asset(symbol, preferred_source=preferred_source)
        if asset is None:
            return None
        return asset, list(asset.chart_points)

    def _limit_unique(self, rows: Sequence[MarketQuotePayload], *, max_items: int) -> list[MarketQuotePayload]:
        unique: list[MarketQuotePayload] = []
        seen: set[tuple[str, str]] = set()
        for item in rows:
            key = (_normalize(item.source_name), _normalize(item.symbol))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
            if len(unique) >= max_items:
                break
        return unique

    def _ordered_providers(self, preferred_source: str | None) -> list[MarketDataProviderPort]:
        if preferred_source is None:
            return list(self.providers)
        preferred = []
        others = []
        normalized = _normalize(preferred_source)
        for provider in self.providers:
            if _normalize(provider.provider_name) == normalized:
                preferred.append(provider)
            else:
                others.append(provider)
        return preferred + others
