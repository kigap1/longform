# API 메모

- 구조: `domain / application / infrastructure / presentation`
- 실행: `uvicorn app.main:app --reload`
- 테스트: `python -m unittest discover -s tests`
- 큐 워커: `celery -A app.infrastructure.queue.celery_app.celery_app worker --loglevel=info`

## Statistics / Market Engine 메모

- 공식 통계 엔진: ECOS, KOSIS, FRED, OECD mock adapter를 통해 추천/검색/시계열/근거 문맥을 제공
- 보조 시장 엔진: Yahoo Finance, Investing.com, Seeking Alpha mock adapter를 통해 자산 검색/시계열을 제공
- 모든 provider는 전용 protocol과 공통 payload를 사용하므로 실제 API 연동 시 adapter만 교체하면 된다
- 실제 연동 전 남은 작업: 인증키 주입, rate limit 대응, 실제 응답 매핑, provider별 통합 테스트

## Claude Script Engine 메모

- `SCRIPT_PROVIDER_MODE=mock|anthropic` 로 mock/real Claude Messages provider를 전환한다
- 요청 DTO의 `provider_mode=mock|real|anthropic` 으로 실행 단위 override도 가능하다
- 프롬프트는 이슈 요약, 검증 통계, 시장 맥락, 사용자 지시, 스타일, 톤, 오디언스를 분리해 조합한다
- 생성과 섹션 재생성 모두 prompt snapshot과 전체 project revision snapshot을 남겨 버전 비교가 가능하다

## Character / Image Engine 메모

- 프로젝트 내 `locked=true` 캐릭터가 있으면 모든 scene 이미지 생성에서 우선 적용한다
- scene별 `image_prompt`는 편집 가능하며, 생성 직전 최종 prompt로 다시 저장된다
- 한국어 인포그래픽 레이아웃 입력, snapshot reference, 사용자 지시를 합쳐 prompt를 구성한다
- 현재는 mock 이미지 생성기지만 adapter는 reference-aware/edit-capable provider 교체를 염두에 두고 설계했다

## Video Preparation Engine 메모

- scene별 최신 이미지와 장면 정보를 기반으로 세로형 숏폼 video prompt를 생성한다
- prepare 단계에서 zip bundle을 만들고, execute 단계에서 mock execution receipt를 기록한다
- `VideoWorkflowPort`는 prepare/execute를 분리해 Veo 계열 provider 교체를 쉽게 한다
- bundle 다운로드 경로는 `/api/videos/bundles/{video_asset_id}?project_id=...` 형식으로 노출된다
