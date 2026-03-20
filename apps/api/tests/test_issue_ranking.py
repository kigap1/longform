from unittest import TestCase

from app.domain.services.issue_ranking import IssueSignal, rank_issue_signals


class IssueRankingTests(TestCase):
    def test_more_recent_and_impactful_issue_ranks_higher(self) -> None:
        ranked = rank_issue_signals(
            [
                IssueSignal("a", "이슈 A", recency_hours=2, article_count=12, source_credibility=0.9, market_impact=0.8),
                IssueSignal("b", "이슈 B", recency_hours=48, article_count=8, source_credibility=0.8, market_impact=0.6),
            ]
        )
        self.assertEqual(ranked[0].issue_id, "a")
        self.assertGreater(ranked[0].score, ranked[1].score)

