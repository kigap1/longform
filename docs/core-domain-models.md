# 코어 도메인 모델 정의

코어 도메인 모델은 영속성 모델과 분리된 순수 데이터 정의로 두었습니다.

- 코드 위치: `apps/api/app/domain/models.py`
- 목적: DB 모델과 무관한 핵심 개념, 규칙, 메서드 정의

## 주요 모델

### 프로젝트
- `Project`
- 프로젝트 전체 컨텍스트의 루트
- 이슈, 통계, 시장 데이터, 근거, 대본, 장면, 자산, 작업, 리비전을 보유

### 이슈 탐색
- `Issue`
- `Article`
- 기사 군집과 우선순위 점수를 관리

### 통계/시장/스냅샷
- `Statistic`, `StatisticPoint`
- `MarketData`, `MarketDataPoint`
- `Snapshot`
- 공식 통계와 보조 시장 데이터를 분리된 타입으로 유지

### 근거/대본/장면
- `Evidence`
- `Script`, `ScriptSection`
- `Scene`
- 근거 매핑과 장면 분해를 도메인 수준에서 명시

### 캐릭터/산출물
- `CharacterProfile`
- `ImageAsset`
- `VideoAsset`
- 캐릭터 잠금과 장면별 자산 이력을 표현

### 작업/설정/버전
- `Job`, `JobLog`
- `AppSetting`
- `ProjectRevision`
- 큐 작업 상태, 로그, 설정, 버전 복원을 독립 모델로 유지

## 내장 규칙

- `Statistic.is_stale(today, freshness_threshold_days)`
- `Evidence.supports_numeric_claim()`
- `Script.all_evidence_ids()`
- `Job.can_retry(max_retries)`

## 설계 의도

- SQLAlchemy ORM은 infrastructure에 남기고, domain은 프레임워크 비의존 상태를 유지
- 테스트는 가능하면 domain 모델과 domain service에서 먼저 수행
- application layer는 이 모델을 조합하고 presentation에 맞는 DTO로 변환

