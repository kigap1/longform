# Fact-based AI Content Studio

한국어 경제·금융·지정학 콘텐츠 제작 파이프라인을 위한 모노레포입니다.  
이슈 탐색, 공식 통계 검증, 시장 데이터/스냅샷 관리, Claude 기반 대본 생성, 캐릭터/이미지 생성, 비디오 준비, 검수와 다운로드까지 하나의 프로젝트 흐름으로 묶습니다.

## 구현 상태

- 백엔드: FastAPI + SQLAlchemy 기반 API, provider port/adapters, 로컬 저장소 추상화, 프로젝트/작업/근거/스냅샷/스크립트/이미지/비디오 서비스 구현
- 프런트엔드: Next.js + React Query 대시보드 UI
- 실연결된 화면: 프로젝트 선택, 대시보드, 이슈 탐색, 통계 검증, 시장 데이터, 스냅샷, 캐릭터, 설정, 작업 로그
- mock 유지 화면: 대본 작업공간, 이미지 워크스페이스, 비디오 워크스페이스, 검수, 다운로드
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

## 모드 전환

### Mock 모드

```env
NEXT_PUBLIC_USE_MOCK_API=true
SCRIPT_PROVIDER_MODE=mock
```

- 모든 화면이 안정적으로 샘플 데이터로 동작합니다.
- 외부 API 키 없이 데모가 가능합니다.

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

## 자주 쓰는 명령

```bash
pnpm dev:web
pnpm dev:api
pnpm test:api
pnpm check
```

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

- Claude, ECOS, KOSIS, FRED, OECD, Yahoo, Investing, Seeking Alpha, 이미지 생성, 비디오 실행은 현재 mock/adapter 경계까지만 구현되어 있습니다
- 스냅샷은 metadata + 저장소 + preview 라우트까지 구현되었지만, 실제 브라우저 자동 캡처는 아직 stub adapter 입니다
- 대본/이미지/비디오/검수 화면은 UI는 준비되어 있지만 아직 전부 실데이터 조회형 화면으로 정리되지는 않았습니다
- 로컬 저장소는 기본적으로 절대 파일 경로를 저장하고, S3 preview URL 생성은 아직 구현되지 않았습니다
- Next.js `snapshots` 페이지는 현재 `<img>` 태그를 사용해서 빌드 시 비차단 경고가 남습니다

## 다음 프로덕션 단계

1. Alembic 마이그레이션 추가와 PostgreSQL 정식 전환
2. 실 provider 인증키 주입과 rate limit/retry/backoff/observability 추가
3. Playwright 기반 SnapshotProvider 구현
4. script/image/video 결과 목록 조회 API 추가 후 남은 프런트 화면 실연결
5. 사용자 인증, 프로젝트 권한, 비밀값 보호 정책 추가
6. S3 업로드 및 signed preview URL 구현
