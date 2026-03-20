from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IssueSignal:
    issue_id: str
    title: str
    recency_hours: float
    article_count: int
    source_credibility: float
    market_impact: float


@dataclass(slots=True)
class IssueRankingWeights:
    recency: float = 0.35
    article_frequency: float = 0.20
    credibility: float = 0.20
    market_impact: float = 0.25


@dataclass(slots=True)
class RankedIssue:
    issue_id: str
    title: str
    score: float
    reasons: list[str]


def _normalize_recency(hours: float) -> float:
    capped = min(max(hours, 0.0), 168.0)
    return round(1 - (capped / 168.0), 4)


def _normalize_frequency(article_count: int) -> float:
    capped = min(max(article_count, 0), 25)
    return round(capped / 25.0, 4)


def calculate_issue_score(signal: IssueSignal, weights: IssueRankingWeights | None = None) -> float:
    active_weights = weights or IssueRankingWeights()
    score = (
        _normalize_recency(signal.recency_hours) * active_weights.recency
        + _normalize_frequency(signal.article_count) * active_weights.article_frequency
        + signal.source_credibility * active_weights.credibility
        + signal.market_impact * active_weights.market_impact
    )
    return round(score, 4)


def build_ranking_reasons(signal: IssueSignal) -> list[str]:
    reasons: list[str] = []
    if signal.recency_hours <= 24:
        reasons.append("최근 24시간 내 보도 집중")
    if signal.article_count >= 10:
        reasons.append("다수 매체에서 중복 보도")
    if signal.source_credibility >= 0.8:
        reasons.append("신뢰도 높은 출처 비중이 높음")
    if signal.market_impact >= 0.75:
        reasons.append("시장 영향도가 높게 평가됨")
    return reasons or ["기본 랭킹 기준 충족"]


def rank_issue_signals(
    signals: list[IssueSignal],
    weights: IssueRankingWeights | None = None,
) -> list[RankedIssue]:
    ranked = [
        RankedIssue(
            issue_id=signal.issue_id,
            title=signal.title,
            score=calculate_issue_score(signal, weights),
            reasons=build_ranking_reasons(signal),
        )
        for signal in signals
    ]
    return sorted(ranked, key=lambda item: item.score, reverse=True)

