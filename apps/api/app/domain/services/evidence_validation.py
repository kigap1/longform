from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class NumericClaim:
    claim_id: str
    text: str
    indicator_code: str | None
    value: float | None
    release_date: date | None
    source_name: str | None


@dataclass(slots=True)
class ValidationIssue:
    claim_id: str
    severity: str
    message: str


def validate_numeric_claims(
    claims: list[NumericClaim],
    *,
    freshness_threshold_days: int,
    today: date,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    observed_values: dict[str, float] = {}

    for claim in claims:
        if claim.indicator_code is None or claim.value is None or claim.release_date is None:
            issues.append(
                ValidationIssue(
                    claim_id=claim.claim_id,
                    severity="error",
                    message="수치 주장에 근거 지표 또는 값이 연결되지 않았습니다.",
                )
            )
            continue

        age_days = (today - claim.release_date).days
        if age_days > freshness_threshold_days:
            issues.append(
                ValidationIssue(
                    claim_id=claim.claim_id,
                    severity="warning",
                    message=f"데이터 기준일이 {age_days}일 전입니다.",
                )
            )

        if claim.indicator_code in observed_values and observed_values[claim.indicator_code] != claim.value:
            issues.append(
                ValidationIssue(
                    claim_id=claim.claim_id,
                    severity="warning",
                    message="동일 지표에서 상충되는 값이 발견되었습니다.",
                )
            )
        else:
            observed_values[claim.indicator_code] = claim.value

    return issues

