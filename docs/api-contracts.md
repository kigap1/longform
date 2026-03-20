# API 계약 목록

모든 API는 FastAPI 프레젠테이션 계층에서 정의되고, 요청/응답 DTO는 `apps/api/app/application/schemas` 아래에 있다.

## 프로젝트

- `GET /api/projects`
  - 응답: 프로젝트 목록
- `POST /api/projects`
  - 요청: 프로젝트 생성 정보
  - 응답: 생성된 프로젝트 요약

## 이슈 탐색

- `GET /api/issues`
  - 응답: 우선순위 이슈 카드 목록 + 페이지 메타
- `POST /api/issues/rank`
  - 요청: 카테고리, 키워드, 프로젝트 범위
  - 응답: 랭킹 계산된 이슈 카드 목록

## 통계 검증

- `POST /api/stats/recommend`
  - 요청: 프로젝트 ID, 이슈 ID, 사용자 지시
  - 응답: 추천 지표 목록
- `POST /api/stats/search`
  - 요청: 키워드, 소스 범위
  - 응답: 검색된 지표 목록
- `GET /api/stats/series`
  - 요청 쿼리: `indicator_code`
  - 응답: 시계열 포인트
- `POST /api/stats/evidence-context`
  - 요청: 프로젝트 ID, 선택 지표 코드 목록, 선택 시장 심볼 목록
  - 응답: 스크립트 생성에 바로 넣을 수 있는 근거 문맥 블록
- `POST /api/stats/fact-check`
  - 요청: 주장 문장 배열, 근거 ID 배열
  - 응답: 주장별 지원 여부, 경고, 연결 근거

## 시장 데이터 / 캡처

- `POST /api/market/search`
  - 요청: 검색어, 자산군
  - 응답: 자산 목록
- `GET /api/market/series`
  - 요청 쿼리: `symbol`
  - 응답: 자산 시계열
- `POST /api/snapshot/capture`
  - 요청: 프로젝트 ID, URL, 메모
  - 응답: 캡처 요약
- `GET /api/snapshot/list`
  - 응답: 스냅샷 목록

## 대본 / 캐릭터 / 이미지 / 영상

- `POST /api/scripts/generate`
  - 요청: 이슈, 선택 통계/시장 컨텍스트, 톤, 오디언스, 스타일 프리셋, 사용자 지시, 선택적 `provider_mode`
  - 응답: 대본, 섹션, 장면, 근거 맵, 버전 정보
- `POST /api/scripts/regenerate-section`
  - 요청: 스크립트 ID, 섹션 ID, 재생성 모드, 사용자 지시, 선택적 `provider_mode`
  - 응답: 갱신된 단일 섹션 + 스크립트 버전
- `GET /api/characters`
  - 응답: 캐릭터 프리셋 목록
- `POST /api/images/generate`
  - 요청: 장면 ID, 선택 캐릭터 ID, prompt override, 한국어 인포그래픽 레이아웃, 참조 스냅샷, 사용자 지시
  - 응답: 이미지 자산 요약
- `POST /api/images/regenerate-scene`
  - 요청: 단일 장면 ID, 선택 캐릭터 ID, prompt override, 레이아웃, 참조 스냅샷, 사용자 지시
  - 응답: 재생성된 이미지 자산 요약
- `PATCH /api/images/scene-prompt`
  - 요청: 장면 ID, 수정된 image prompt
  - 응답: 장면별 최신 image prompt
- `POST /api/videos/prepare`
  - 요청: 장면 ID 목록, 세로형 비디오 지시, 사용자 지시
  - 응답: scene별 video bundle 목록 + 다운로드 경로
- `POST /api/videos/execute`
  - 요청: video asset ID 목록, 사용자 지시
  - 응답: execution 상태, provider job ID, mock output path
- `GET /api/videos/bundles/{video_asset_id}`
  - 요청 쿼리: `project_id`
  - 응답: zip bundle 파일 다운로드

## 근거 / 설정 / 작업

- `GET /api/evidence/report/{project_id}`
  - 응답: 프로젝트 근거 리포트
- `GET /api/settings`
  - 응답: 설정 목록
- `PUT /api/settings`
  - 요청: 설정 key/value
  - 응답: 저장 완료 메시지
- `GET /api/jobs`
  - 응답: 작업 목록
- `GET /api/jobs/{job_id}`
  - 응답: 작업 요약 + 로그

## 계약 원칙

- 프런트 UI는 이 계약만 의존하고 제공자 세부 구현을 모른다.
- 숫자 주장 검증 결과는 반드시 근거 참조를 포함한다.
- 장기 작업은 즉시 결과 대신 Job 상태 조회 구조로 확장 가능하도록 설계한다.
- 통계 응답은 공식 통계 여부와 신선도 판단에 필요한 메타데이터를 포함한다.
- 시장 응답은 보조 자료임을 유지하며, 공식 통계와 섞이지 않도록 source note를 포함한다.
- 스크립트 생성 프롬프트는 이슈 요약, 검증 통계, 시장 맥락, 사용자 지시, 스타일, 톤, 오디언스를 명시적으로 분리한다.
- 스크립트 생성/재생성은 prompt snapshot과 전체 결과 snapshot을 함께 저장해 버전 비교를 지원한다.
- 이미지 생성은 장면 프롬프트, 캐릭터 프로필, 레이아웃, snapshot reference를 합쳐 최종 prompt를 만들고, scene/image asset/revision에 각각 저장한다.
- 비디오 준비는 장면별 prompt/motion/bundle을 만들고, 실행은 별도 job으로 추적하며, mock 단계에서는 execution receipt를 저장한다.
