from datetime import date, timedelta
from unittest import TestCase

from app.domain.services.evidence_validation import NumericClaim, validate_numeric_claims


class EvidenceValidationTests(TestCase):
    def test_missing_mapping_and_stale_data_raise_issues(self) -> None:
        today = date(2026, 3, 20)
        claims = [
            NumericClaim(
                claim_id="claim-1",
                text="기준금리가 3.25%다.",
                indicator_code=None,
                value=None,
                release_date=None,
                source_name=None,
            ),
            NumericClaim(
                claim_id="claim-2",
                text="물가가 114.2다.",
                indicator_code="CPI",
                value=114.2,
                release_date=today - timedelta(days=60),
                source_name="KOSIS",
            ),
        ]
        issues = validate_numeric_claims(claims, freshness_threshold_days=45, today=today)
        messages = [issue.message for issue in issues]
        self.assertEqual(len(issues), 2)
        self.assertIn("수치 주장에 근거 지표 또는 값이 연결되지 않았습니다.", messages)
        self.assertTrue(any("60일 전" in message for message in messages))

