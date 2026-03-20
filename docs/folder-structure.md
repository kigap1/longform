# 최종 폴더 구조

```text
longf/
├─ apps/
│  ├─ api/
│  │  ├─ app/
│  │  │  ├─ application/
│  │  │  │  ├─ schemas/
│  │  │  │  └─ services.py
│  │  │  ├─ core/
│  │  │  │  ├─ config.py
│  │  │  │  └─ database.py
│  │  │  ├─ domain/
│  │  │  │  ├─ enums.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ provider_interfaces.py
│  │  │  │  └─ services/
│  │  │  ├─ infrastructure/
│  │  │  │  ├─ db/
│  │  │  │  ├─ providers/
│  │  │  │  ├─ queue/
│  │  │  │  └─ storage/
│  │  │  ├─ presentation/
│  │  │  │  └─ api/
│  │  │  └─ main.py
│  │  ├─ tests/
│  │  ├─ pyproject.toml
│  │  └─ README.md
│  └─ web/
│     ├─ app/
│     ├─ components/
│     ├─ lib/
│     ├─ .eslintrc.json
│     ├─ package.json
│     ├─ tailwind.config.ts
│     └─ tsconfig.json
├─ docs/
│  ├─ adr/
│  │  └─ 0001-phase-1-foundation.md
│  ├─ api-contracts.md
│  ├─ architecture.md
│  ├─ core-domain-models.md
│  ├─ database-schema.md
│  ├─ folder-structure.md
│  ├─ provider-adapter-interfaces.md
│  └─ queue-job-model.md
├─ .env.example
├─ docker-compose.yml
├─ package.json
├─ pnpm-workspace.yaml
└─ README.md
```

## 구조 원칙

- `apps/api/app/domain`: 외부 프레임워크에 의존하지 않는 핵심 모델과 규칙
- `apps/api/app/application`: 유스케이스 조합과 API 입출력 계약
- `apps/api/app/infrastructure`: DB, 큐, 저장소, 외부 제공자 어댑터
- `apps/api/app/presentation`: FastAPI 라우터
- `apps/web`: 한국어 전용 대시보드 UI
- `docs`: Phase 1 설계 산출물

