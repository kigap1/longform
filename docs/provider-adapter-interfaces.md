# 제공자 어댑터 인터페이스

## 코드 위치

- 인터페이스: `apps/api/app/domain/provider_interfaces.py`
- 예시 구현: `apps/api/app/infrastructure/providers/adapters.py`

## 포트 목록

### 뉴스 제공자
- `NewsProviderPort`
- 책임: 최신 기사 수집
- 출력: `NewsArticlePayload`

### 통계 제공자
- `StatisticsProviderPort`
- 전용 세부 포트: `EcosProviderPort`, `KosisProviderPort`, `FredProviderPort`, `OecdProviderPort`
- 책임: 지표 검색, 이슈 기반 지표 추천
- 추가 계약: 단건 지표 조회, 시계열 조회
- 출력: `IndicatorPayload`
- 대상 제공자: ECOS, KOSIS, FRED, OECD

### 시장 데이터 제공자
- `MarketDataProviderPort`
- 전용 세부 포트: `YahooFinanceProviderPort`, `InvestingProviderPort`, `SeekingAlphaProviderPort`
- 책임: 자산 검색과 시세/차트 데이터 제공
- 추가 계약: 단건 자산 조회, 시계열 조회
- 출력: `MarketQuotePayload`
- 대상 제공자: Yahoo Finance, Investing.com, Seeking Alpha

### 스냅샷 제공자
- `SnapshotProviderPort`
- 책임: URL 또는 영역 캡처
- 출력: `SnapshotPayload`

### 대본 모델 제공자
- `ScriptModelPort`
- Claude 전용 세부 포트: `ClaudeMessagesProviderPort`
- 책임: 이슈 + 근거 컨텍스트 기반 스크립트 생성
- 추가 계약: 섹션 재생성, Messages API 요청/응답 변환
- 출력: `ScriptGenerationPayload`, `ScriptSectionPayload`
- 대상 제공자: Claude

### 이미지 생성 제공자
- `ImageGenerationPort`
- 책임: 장면별 이미지 생성과 기존 장면 이미지 edit/regenerate
- 입력: `SceneImageGenerationRequestPayload`
- 출력: `ImageGenerationPayload`
- 현재 구현: `MockImageGeneratorAdapter`
- 미래 대상: Nano Banana 스타일 reference-aware/edit-capable provider

### 영상 워크플로 제공자
- `VideoWorkflowPort`
- 책임: 장면별 video prompt/bundle 준비와 bundle 실행
- 입력: `SceneVideoPreparationRequestPayload`, `VideoExecutionRequestPayload`
- 출력: `VideoPreparationPayload`, `VideoExecutionPayload`
- 대상 제공자: Veo 3.1 또는 대체 워크플로

## 설계 원칙

- 코어 도메인은 제공자 이름, 인증 방식, HTTP 세부 구현을 모른다.
- 제공자 교체는 adapter 구현 교체로 끝나야 한다.
- 실제 구현이 없는 영역은 mock adapter와 TODO 계약으로 먼저 고정한다.
- 공식 통계 제공자와 보조 시장 데이터 제공자는 서로 다른 포트 책임으로 유지한다.
- 시계열 포맷은 `TimeSeriesPointPayload`로 통일해 엔진과 API 응답을 단순화한다.
- 근거 문맥은 통계와 시장 데이터를 함께 조합하되, 시장 데이터는 항상 보조 자료로 표시한다.

## 현재 예시 구현 상태

- 통계: `EcosAdapter`, `KosisAdapter`, `FredAdapter`, `OecdAdapter`
- 시장: `YahooFinanceAdapter`, `InvestingAdapter`, `SeekingAlphaAdapter`
- 스냅샷: `MockSnapshotAdapter`
- 대본: `ClaudeMessagesMockAdapter`, `ClaudeMessagesAPIAdapter`
- 이미지: `MockImageGeneratorAdapter`
- 영상: `MockVeoWorkflowAdapter`

## 실제 연동 시 남은 일

- ECOS/KOSIS/FRED/OECD: API 키 주입, 실패 재시도, 응답 매핑, 날짜/빈도 정규화
- Yahoo/Investing/Seeking Alpha: 사용 가능한 공식/비공식 데이터 경로 확인, 속도 제한과 차단 대응
- Claude Messages API: 모델명/버전 운영 정책 확정, 요청 단위 provider mode 운영 규칙 확정, 응답 JSON 실패 시 재시도/복구 전략 추가
- 이미지 제공자: reference image 입력, edit API, 업로드 자산 처리, provider별 응답 URL/파일 저장 정책 확정
- 비디오 제공자: bundle 업로드/참조 이미지 입력, provider job polling, 최종 mp4 저장 정책, 실패 재시도/콜백 처리 확정
- 모든 제공자: 네트워크 오류와 빈 응답 처리, 관측 가능성 로그, 캐시/백오프 정책 추가
- 공통: mock sample data를 실제 응답 DTO로 교체하고, provider별 통합 테스트를 별도 추가
