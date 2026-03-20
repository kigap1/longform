from datetime import date
from unittest import TestCase

from app.domain.services.data_engines import MarketDataEngine, StatisticsVerificationEngine
from app.infrastructure.providers.adapters import (
    EcosAdapter,
    FredAdapter,
    InvestingAdapter,
    KosisAdapter,
    OecdAdapter,
    SeekingAlphaAdapter,
    YahooFinanceAdapter,
)


class StatisticsMarketEngineTests(TestCase):
    def setUp(self) -> None:
        self.statistics_engine = StatisticsVerificationEngine(
            providers=[EcosAdapter(), KosisAdapter(), FredAdapter(), OecdAdapter()]
        )
        self.market_engine = MarketDataEngine(
            providers=[YahooFinanceAdapter(), InvestingAdapter(), SeekingAlphaAdapter()]
        )

    def test_indicator_recommendation_collects_official_providers(self) -> None:
        results = self.statistics_engine.recommend_indicators("미국 금리와 원화 변동성")
        provider_names = {item.source_name for item in results}
        self.assertIn("ECOS", provider_names)
        self.assertIn("FRED", provider_names)

    def test_indicator_search_respects_source_scope(self) -> None:
        results = self.statistics_engine.search_indicators("물가", source_scope=["KOSIS"])
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual({item.source_name for item in results}, {"KOSIS"})

    def test_stale_detection_and_evidence_context_builder(self) -> None:
        oecd_indicator = self.statistics_engine.get_indicator("CLI_AMPLITUDENORM", preferred_source="OECD")
        fx_asset = self.market_engine.get_asset("KRW=X", preferred_source="Yahoo Finance")
        self.assertIsNotNone(oecd_indicator)
        self.assertIsNotNone(fx_asset)

        context_items, combined_context = self.statistics_engine.build_evidence_context(
            indicators=[oecd_indicator] if oecd_indicator else [],
            market_assets=[fx_asset] if fx_asset else [],
            freshness_threshold_days=45,
            today=date(2026, 3, 20),
        )

        self.assertEqual(len(context_items), 2)
        self.assertTrue(context_items[0].stale)
        self.assertIn("[공식 통계]", combined_context)
        self.assertIn("[보조 시장자료]", combined_context)

    def test_market_search_and_series_return_supplementary_assets(self) -> None:
        results = self.market_engine.search_assets("유가", asset_class="commodities", source_scope=["Investing.com"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source_name, "Investing.com")

        series_payload = self.market_engine.get_time_series("CL", preferred_source="Investing.com")
        self.assertIsNotNone(series_payload)
        asset, points = series_payload if series_payload is not None else (None, [])
        self.assertEqual(asset.symbol if asset else None, "CL")
        self.assertEqual(len(points), 6)
