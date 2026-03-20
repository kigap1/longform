# Fact-based AI Content Studio

한국어 경제·금융·지정학 콘텐츠 제작 파이프라인을 위한 모노레포입니다.  
이슈 탐색, 공식 통계 검증, 시장 데이터/스냅샷 관리, OpenAI/Claude/Gemini 선택형 대본 생성, 캐릭터/이미지 생성, 비디오 준비, Kling AI 비디오 브리지 경계, 검수와 다운로드까지 하나의 프로젝트 흐름으로 묶습니다.

## 구현 상태

- 백엔드: FastAPI + SQLAlchemy 기반 API, provider port/adapters, 로컬 저장소 추상화, 프로젝트/작업/근거/스냅샷/스크립트/이미지/비디오 서비스 구현
- 프런트엔드: Next.js + React Query 대시보드 UI
- 실연결된 화면: 프로젝트 선택, 대시보드, 이슈 탐색, 통계 검증, 시장 데이터, 스냅샷, 캐릭터, AI 연결, 설정, 작업 로그
- 생성 단계: 대본/이미지/비디오 화면에서 OpenAI, Claude, Gemini, Kling(비디오 전용) 선택 UI와 mock 생성 흐름 연결
- fallback 전략: `NEXT_PUBLIC_USE_MOCK_API=true` 이면 전체 UI가 mock 모드로 동작하고, `false` 이면 가능한 화면부터 FastAPI 실데이터를 사용합니다

## 빠른 시작

### 1. 요구 사항

- Node.js 20+
- pnpm 10+
- Python 3.11+ 권장, 3.12 권장

### 2. 환경 변수

```bash
cp .env.example .env
```

기본 예시는 빠른 실행을 위해 SQLite + 로컬 저장소 + mock provider 기준입니다.
OpenAI/Claude/Gemini/Kling 키는 비워둔 상태로 시작해도 됩니다. 이 경우 대본/이미지/비디오 단계는 mock provider로 먼저 검증할 수 있습니다.

### 3. 의존성 설치

```bash
pnpm install
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd ../..
```

### 4. 백엔드 실행

```bash
pnpm dev:api
```

백엔드는 처음 실행 시 SQLite DB를 만들고 데모 프로젝트/설정/근거/작업을 seed 합니다.

### 5. 프런트엔드 실행

```bash
pnpm dev:web
```

브라우저에서 `http://localhost:3000` 을 엽니다.

### 원커맨드 실행

```bash
pnpm dev
```

- 프런트와 백엔드를 함께 실행합니다.
- `apps/api/.venv` 가 있으면 그 Python을 우선 사용합니다.
- 종료는 `Ctrl+C` 한 번이면 둘 다 같이 멈춥니다.

## 모드 전환

### Mock 모드

```env
NEXT_PUBLIC_USE_MOCK_API=true
SCRIPT_PROVIDER_MODE=mock
IMAGE_PROVIDER_MODE=mock
VIDEO_PROVIDER_MODE=mock
```

- 모든 화면이 안정적으로 샘플 데이터로 동작합니다.
- 외부 API 키 없이 데모가 가능합니다.
- OpenAI, Claude, Gemini, Kling 선택 UI는 보이지만 실제 네트워크 호출 대신 mock provider로 테스트합니다.

### Real API 모드

```env
NEXT_PUBLIC_USE_MOCK_API=false
SCRIPT_PROVIDER_MODE=mock
```

- 프런트는 가능한 화면부터 FastAPI 응답을 사용합니다.
- 현재 연결된 화면:
  - 대시보드
  - 이슈 탐색
  - 통계 검증
  - 시장 데이터
  - 스냅샷
  - 캐릭터
  - 설정
  - 작업 로그
- 대본/이미지/비디오는 현재도 mock provider를 먼저 타지만, 선택한 provider id가 서비스 레이어와 작업 로그까지 반영됩니다.
- `AI 연결` 메뉴에서 키, 기본 공급자, 기본 모드를 GUI로 저장할 수 있습니다.

## 자주 쓰는 명령

```bash
pnpm dev:web
pnpm dev:api
pnpm test:api
pnpm check
```

- `pnpm dev:api`, `pnpm test:api` 는 `apps/api/.venv` 가 있으면 해당 Python을 우선 사용합니다.

## 테스트

기본 검증은 백엔드 서비스 테스트와 스모크 테스트를 포함합니다.

```bash
cd apps/api
python3 -m unittest discover -s tests
```

프런트엔드는 타입체크와 프로덕션 빌드로 검증합니다.

```bash
pnpm typecheck:web
pnpm build:web
```

2026-03-20 기준으로 실제로 검증한 범위:

- OpenAI/Claude/Gemini/Kling provider 선택이 대본/이미지/비디오 서비스에 반영되는 mock 테스트 통과
- Claude 이미지/비디오 선택 시 명확한 boundary error 반환 확인
- Kling real 모드는 브리지형 submit 경계와 로컬 테스트 서버 기준으로 요청/응답 매핑 검증
- 뉴스 랭킹 버튼과 이슈 재계산 UI 액션 연결 확인
- `pnpm --filter web typecheck`, `pnpm --filter web build`, `python3 -m unittest discover -s tests` 통과

## 주요 파일 트리

```text
.
├── .env.example
├── README.md
├── package.json
├── pnpm-workspace.yaml
├── apps
│   ├── api
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── app
│   │   │   ├── application
│   │   │   │   ├── schemas
│   │   │   │   └── services.py
│   │   │   ├── core
│   │   │   ├── domain
│   │   │   │   ├── provider_interfaces.py
│   │   │   │   └── services
│   │   │   ├── infrastructure
│   │   │   │   ├── db
│   │   │   │   ├── providers
│   │   │   │   └── storage
│   │   │   ├── main.py
│   │   │   └── presentation
│   │   │       └── api
│   │   └── tests
│   └── web
│       ├── app
│       ├── components
│       ├── lib
│       │   ├── api
│       │   │   ├── client.ts
│       │   │   ├── hooks.ts
│       │   │   ├── mock-api.ts
│       │   │   └── types.ts
│       │   └── stores
│       └── package.json
├── docs
│   ├── api-contracts.md
│   ├── image-pipeline-design.md
│   ├── provider-adapter-interfaces.md
│   ├── script-prompting-strategy.md
│   ├── snapshot-capture-integration.md
│   └── video-pipeline-design.md
└── docker-compose.yml
```

## 알려진 제한 사항

- ECOS, KOSIS, FRED, OECD, Yahoo, Investing, Seeking Alpha는 현재 mock/adapter 경계까지만 구현되어 있습니다
- OpenAI/Gemini는 설정값과 선택 경로, typed adapter boundary, mock 테스트까지 구현했지만 실 API 호출은 아직 연결하지 않았습니다
- Claude는 스크립트 단계 real adapter가 준비되어 있지만, 이미지/비디오 단계는 미지원으로 명시적으로 막아두었습니다
- Kling은 공식 글로벌 웹앱에서 확인된 base URL을 기본값으로 넣었고, 비디오 real 모드는 submit/status/result 경로를 공식 경로 또는 사내 브리지로 직접 주입해야 합니다
- 스냅샷은 metadata + 저장소 + preview 라우트까지 구현되었지만, 실제 브라우저 자동 캡처는 아직 stub adapter 입니다
- 대본/이미지/비디오 화면은 생성 액션은 연결되었지만, 장기적으로는 목록 조회와 버전 브라우징 API를 더 보강해야 합니다
- 로컬 저장소는 기본적으로 절대 파일 경로를 저장하고, S3 preview URL 생성은 아직 구현되지 않았습니다

## 다음 프로덕션 단계

1. Alembic 마이그레이션 추가와 PostgreSQL 정식 전환
2. OpenAI/Gemini 실 adapter 확정 후 rate limit/retry/backoff/observability 추가
3. Claude real mode 운영 전 malformed JSON 복구와 timeout 정책 보강
4. Playwright 기반 SnapshotProvider 구현
5. script/image/video 결과 목록 조회 API와 버전 브라우징 화면 추가
6. 사용자 인증, 프로젝트 권한, 비밀값 보호 정책 추가
7. S3 업로드 및 signed preview URL 구현
