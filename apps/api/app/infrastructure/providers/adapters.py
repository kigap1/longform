from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from urllib.parse import urlparse

from app.domain.enums import IssueCategory
from app.domain.provider_interfaces import (
    EcosProviderPort,
    FredProviderPort,
    ImageGenerationPayload,
    ImageGenerationPort,
    IndicatorPayload,
    InvestingProviderPort,
    KosisProviderPort,
    MarketQuotePayload,
    OecdProviderPort,
    NewsArticlePayload,
    NewsProviderPort,
    SeekingAlphaProviderPort,
    SceneImageGenerationRequestPayload,
    SceneVideoPreparationRequestPayload,
    SnapshotPayload,
    SnapshotProviderPort,
    TimeSeriesPointPayload,
    VideoExecutionPayload,
    VideoExecutionRequestPayload,
    VideoPreparationPayload,
    VideoWorkflowPort,
    YahooFinanceProviderPort,
)
from app.infrastructure.providers.sample_data import get_market_sample_data, get_statistics_sample_data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str) -> str:
    return text.strip().lower()


def _matches_keyword(keyword: str, values: list[str]) -> bool:
    normalized_keyword = _normalize(keyword)
    if not normalized_keyword:
        return True
    return any(normalized_keyword in _normalize(value) or _normalize(value) in normalized_keyword for value in values)


@dataclass(slots=True)
class MockKoreanNewsAdapter(NewsProviderPort):
    provider_name: str = "국내 뉴스 모의 제공자"

    def fetch_latest(self, keyword: str | None = None) -> list[NewsArticlePayload]:
        _ = keyword
        now = datetime.now(timezone.utc)
        return [
            NewsArticlePayload(
                title="미국 금리 인하 기대에 원화 변동성 확대",
                source_name="연합뉴스",
                published_at=now,
                url="https://example.com/news/kr-1",
                summary="환율과 외국인 자금 흐름이 함께 주목받고 있습니다.",
                category=IssueCategory.ECONOMY,
                credibility_score=0.9,
            ),
            NewsArticlePayload(
                title="원·달러 환율 상승, 증시 외국인 수급 압박",
                source_name="한국경제",
                published_at=now,
                url="https://example.com/news/kr-2",
                summary="금리 기대 변화가 환율과 위험자산에 동시에 반영되고 있습니다.",
                category=IssueCategory.INVESTING,
                credibility_score=0.83,
            ),
            NewsArticlePayload(
                title="중동 해상 리스크에 국제유가 반등",
                source_name="매일경제",
                published_at=now,
                url="https://example.com/news/kr-3",
                summary="지정학 긴장으로 에너지 가격 불확실성이 커졌습니다.",
                category=IssueCategory.GEOPOLITICS,
                credibility_score=0.82,
            ),
        ]


@dataclass(slots=True)
class MockGlobalNewsAdapter(NewsProviderPort):
    provider_name: str = "글로벌 뉴스 모의 제공자"

    def fetch_latest(self, keyword: str | None = None) -> list[NewsArticlePayload]:
        _ = keyword
        now = datetime.now(timezone.utc)
        return [
            NewsArticlePayload(
                title="Fed easing bets ripple through Asian FX markets",
                source_name="Reuters",
                published_at=now,
                url="https://example.com/news/global-1",
                summary="Asian currencies react to shifting rate expectations.",
                category=IssueCategory.ECONOMY,
                credibility_score=0.91,
            ),
            NewsArticlePayload(
                title="Oil rebounds as shipping security concerns rise in Middle East",
                source_name="Bloomberg",
                published_at=now,
                url="https://example.com/news/global-2",
                summary="Crude prices pick up as supply concerns return.",
                category=IssueCategory.GEOPOLITICS,
                credibility_score=0.88,
            ),
            NewsArticlePayload(
                title="China property weakness clouds Korea export outlook",
                source_name="WSJ",
                published_at=now,
                url="https://example.com/news/global-3",
                summary="Korean exporters face slower demand from China.",
                category=IssueCategory.INVESTING,
                credibility_score=0.85,
            ),
        ]


class _BaseStatisticsAdapter:
    provider_name: str
    source_url: str

    def _rows(self) -> list[IndicatorPayload]:
        return [
            IndicatorPayload(
                code=row["code"],
                name=row["name"],
                source_name=self.provider_name,
                source_url=self.source_url,
                description=row["description"],
                latest_value=row["latest_value"],
                previous_value=row["previous_value"],
                release_date=row["release_date"],
                frequency=row["frequency"],
                unit=row["unit"],
                tags=row.get("tags", []),
                recommended_reason=row.get("recommended_reason"),
                series_points=[
                    TimeSeriesPointPayload(date=point["date"], value=point["value"]) for point in row["series_points"]
                ],
            )
            for row in get_statistics_sample_data(self.provider_name)
        ]

    def search_indicators(self, keyword: str) -> list[IndicatorPayload]:
        rows = self._rows()
        matched = [
            item for item in rows if _matches_keyword(keyword, [item.code, item.name, item.description, *item.tags])
        ]
        return matched or rows[:2]

    def recommend_indicators(self, issue_title: str) -> list[IndicatorPayload]:
        rows = self._rows()
        matched = [
            item for item in rows if _matches_keyword(issue_title, [issue_title, item.name, item.description, *item.tags])
        ]
        return matched or rows[:1]

    def get_indicator(self, indicator_code: str) -> IndicatorPayload | None:
        normalized_code = _normalize(indicator_code)
        for item in self._rows():
            if normalized_code == _normalize(item.code):
                return item
        return None

    def get_time_series(self, indicator_code: str) -> list[TimeSeriesPointPayload]:
        indicator = self.get_indicator(indicator_code)
        return list(indicator.series_points) if indicator else []


@dataclass(slots=True)
class EcosAdapter(_BaseStatisticsAdapter, EcosProviderPort):
    provider_name: str = "ECOS"
    source_url: str = "https://ecos.bok.or.kr"


@dataclass(slots=True)
class KosisAdapter(_BaseStatisticsAdapter, KosisProviderPort):
    provider_name: str = "KOSIS"
    source_url: str = "https://kosis.kr"


@dataclass(slots=True)
class FredAdapter(_BaseStatisticsAdapter, FredProviderPort):
    provider_name: str = "FRED"
    source_url: str = "https://fred.stlouisfed.org"


@dataclass(slots=True)
class OecdAdapter(_BaseStatisticsAdapter, OecdProviderPort):
    provider_name: str = "OECD"
    source_url: str = "https://stats.oecd.org"


class _BaseMarketAdapter:
    provider_name: str
    source_url: str

    def _rows(self) -> list[MarketQuotePayload]:
        return [
            MarketQuotePayload(
                symbol=row["symbol"],
                display_name=row["display_name"],
                asset_class=row["asset_class"],
                source_name=self.provider_name,
                source_url=self.source_url,
                latest_value=row["latest_value"],
                change_percent=row["change_percent"],
                as_of=row["as_of"],
                currency=row["currency"],
                note=row.get("note", ""),
                tags=row.get("tags", []),
                chart_points=[
                    TimeSeriesPointPayload(date=point["date"], value=point["value"]) for point in row["chart_points"]
                ],
            )
            for row in get_market_sample_data(self.provider_name)
        ]

    def search_assets(self, query: str, asset_class: str | None = None) -> list[MarketQuotePayload]:
        rows = self._rows()
        matched = [
            item
            for item in rows
            if (asset_class is None or item.asset_class == asset_class)
            and _matches_keyword(query, [item.symbol, item.display_name, item.note, *item.tags])
        ]
        if matched:
            return matched
        if asset_class is None:
            return rows[:2]
        return [item for item in rows if item.asset_class == asset_class][:2]

    def get_asset(self, symbol: str) -> MarketQuotePayload | None:
        normalized_symbol = _normalize(symbol)
        for item in self._rows():
            if normalized_symbol == _normalize(item.symbol):
                return item
        return None

    def get_time_series(self, symbol: str) -> list[TimeSeriesPointPayload]:
        asset = self.get_asset(symbol)
        return list(asset.chart_points) if asset else []


@dataclass(slots=True)
class YahooFinanceAdapter(_BaseMarketAdapter, YahooFinanceProviderPort):
    provider_name: str = "Yahoo Finance"
    source_url: str = "https://finance.yahoo.com"


@dataclass(slots=True)
class InvestingAdapter(_BaseMarketAdapter, InvestingProviderPort):
    provider_name: str = "Investing.com"
    source_url: str = "https://www.investing.com"


@dataclass(slots=True)
class SeekingAlphaAdapter(_BaseMarketAdapter, SeekingAlphaProviderPort):
    provider_name: str = "Seeking Alpha"
    source_url: str = "https://seekingalpha.com"


@dataclass(slots=True)
class MockSnapshotAdapter(SnapshotProviderPort):
    provider_name: str = "Mock Snapshot"
    mode: str = "stub"
    integration_boundary_note: str = (
        "실제 브라우저 캡처는 아직 연결되지 않았습니다. 현재는 stub 렌더를 저장하고 provider 경계만 고정합니다."
    )

    def capture(self, url: str, note: str = "", source_title: str | None = None) -> SnapshotPayload:
        parsed = urlparse(url)
        derived_title = source_title or (parsed.netloc or "Snapshot Source")
        svg = _build_snapshot_stub_svg(title=derived_title, url=url, note=note or "자동 캡처 예시")
        return SnapshotPayload(
            title=f"{derived_title} 캡처",
            source_title=derived_title,
            source_url=url,
            captured_at=_now_iso(),
            note=note or "자동 캡처 예시",
            image_url="https://placehold.co/1200x675/png?text=Snapshot",
            image_bytes=svg.encode("utf-8"),
            content_type="image/svg+xml",
            capture_mode=self.mode,
            integration_boundary_note=self.integration_boundary_note,
        )


@dataclass(slots=True)
class MockImageGeneratorAdapter(ImageGenerationPort):
    provider_name: str = "Mock Image Generator"
    mode: str = "mock"

    def generate_image(self, payload: SceneImageGenerationRequestPayload) -> ImageGenerationPayload:
        # TODO: Nano Banana 스타일 제공자 연동 시 reference image/scene edit 입력을 실제 API payload로 매핑한다.
        return ImageGenerationPayload(
            scene_id=payload.scene_id,
            prompt=payload.prompt_override or payload.base_image_prompt,
            revised_prompt=payload.prompt_override or payload.base_image_prompt,
            asset_url=f"https://placehold.co/1024x1536/png?text={payload.scene_id}",
            thumbnail_url=f"https://placehold.co/256x384/png?text={payload.scene_id}",
            provider_name=self.provider_name,
            reference_snapshot_ids=[item.snapshot_id for item in payload.reference_snapshots],
        )

    def edit_image(self, payload: SceneImageGenerationRequestPayload) -> ImageGenerationPayload:
        generated = self.generate_image(payload)
        return ImageGenerationPayload(
            scene_id=generated.scene_id,
            prompt=generated.prompt,
            revised_prompt=f"{generated.revised_prompt}\n[편집 모드] 기존 장면을 유지하면서 프롬프트를 갱신",
            asset_url=generated.asset_url,
            thumbnail_url=generated.thumbnail_url,
            provider_name=generated.provider_name,
            reference_snapshot_ids=generated.reference_snapshot_ids,
        )


@dataclass(slots=True)
class MockVeoWorkflowAdapter(VideoWorkflowPort):
    provider_name: str = "Mock Veo Workflow"
    mode: str = "mock"

    def prepare_scene(self, payload: SceneVideoPreparationRequestPayload) -> VideoPreparationPayload:
        return VideoPreparationPayload(
            scene_id=payload.scene_id,
            prompt=(
                f"{payload.scene_title} 영상 준비 프롬프트\n"
                f"{payload.image_prompt}\n"
                f"비율 {payload.vertical_instructions.aspect_ratio}, "
                f"길이 {payload.vertical_instructions.duration_seconds}초"
            ),
            motion_notes="인포그래픽 숫자 강조, 부드러운 줌 인, 자막 안전영역 유지, 앵커 시선 유지",
            bundle_path=payload.bundle_path,
            download_path=payload.download_path,
            image_asset_id=payload.image_asset_id,
            provider_name=self.provider_name,
        )

    def execute_bundle(self, payload: VideoExecutionRequestPayload) -> VideoExecutionPayload:
        output_path = payload.bundle_path.replace(".zip", "-mock-execution.json")
        return VideoExecutionPayload(
            video_asset_id=payload.video_asset_id,
            scene_id=payload.scene_id,
            provider_job_id=f"mock-veo-{payload.video_asset_id}",
            status="success",
            output_path=output_path,
            bundle_path=payload.bundle_path,
            provider_name=self.provider_name,
        )


def _build_snapshot_stub_svg(*, title: str, url: str, note: str) -> str:
    safe_title = escape(title)
    safe_url = escape(url)
    safe_note = escape(note)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-label="{safe_title}">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#0f766e" />
    </linearGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#bg)" rx="32" />
  <rect x="54" y="54" width="1092" height="567" rx="28" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)" />
  <text x="84" y="120" fill="#f8fafc" font-size="40" font-family="Arial, sans-serif" font-weight="700">{safe_title}</text>
  <text x="84" y="168" fill="#cbd5e1" font-size="22" font-family="Arial, sans-serif">Stub Snapshot Capture</text>
  <text x="84" y="230" fill="#e2e8f0" font-size="20" font-family="Arial, sans-serif">Source URL</text>
  <text x="84" y="266" fill="#93c5fd" font-size="22" font-family="Arial, sans-serif">{safe_url}</text>
  <text x="84" y="340" fill="#e2e8f0" font-size="20" font-family="Arial, sans-serif">Note</text>
  <text x="84" y="376" fill="#f8fafc" font-size="24" font-family="Arial, sans-serif">{safe_note}</text>
  <rect x="84" y="438" width="1032" height="130" rx="20" fill="rgba(15,23,42,0.38)" stroke="rgba(148,163,184,0.24)" />
  <text x="112" y="486" fill="#fef08a" font-size="20" font-family="Arial, sans-serif">Integration Boundary</text>
  <text x="112" y="522" fill="#e2e8f0" font-size="22" font-family="Arial, sans-serif">Full browser capture not implemented yet.</text>
  <text x="112" y="554" fill="#cbd5e1" font-size="18" font-family="Arial, sans-serif">Swap this adapter with a Playwright/Chromium capture provider later.</text>
</svg>
""".strip()
