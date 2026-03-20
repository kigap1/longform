export const projects = [
  {
    id: "project-1",
    name: "미국 금리와 원화 변동성",
    summary: "금리, 환율, 외국인 수급을 함께 추적하는 메인 프로젝트",
    stage: "대본 생성",
    updatedAt: "2026-03-20 10:28"
  },
  {
    id: "project-2",
    name: "중동 리스크와 국제유가",
    summary: "유가와 물류 리스크를 중심으로 지정학 이슈를 추적",
    stage: "통계 검증",
    updatedAt: "2026-03-20 09:52"
  },
  {
    id: "project-3",
    name: "중국 경기 둔화와 한국 수출",
    summary: "수출주, 경기선행지수, 중국 경기 지표를 연결",
    stage: "이미지 생성",
    updatedAt: "2026-03-19 18:10"
  }
] as const;

export const dashboardMetrics = [
  { label: "활성 프로젝트", value: "12", change: "+2", tone: "accent" },
  { label: "검증 완료 근거", value: "248", change: "+18", tone: "navy" },
  { label: "대기 작업", value: "7", change: "실행 중 3", tone: "warn" },
  { label: "완료 산출물", value: "64", change: "오늘 9건", tone: "accent" }
] as const;

export const issueCards = [
  {
    id: "issue-1",
    title: "미국 금리 인하 기대와 원화 변동성",
    category: "경제",
    score: 0.89,
    reasons: ["최근 24시간 내 보도 집중", "다수 매체에서 중복 보도", "시장 영향도가 높게 평가됨"]
  },
  {
    id: "issue-2",
    title: "중동 물류 리스크와 유가 재상승",
    category: "지정학",
    score: 0.84,
    reasons: ["원자재 민감 자산에 파급", "국제 기사와 국내 기사 동시 확산"]
  },
  {
    id: "issue-3",
    title: "중국 부동산 둔화와 한국 수출 부담",
    category: "투자",
    score: 0.76,
    reasons: ["수출주 실적 영향 가능성", "공식 지표 확인 필요"]
  }
] as const;

export const statisticsRows = [
  {
    code: "722Y001",
    name: "한국은행 기준금리",
    source: "ECOS",
    latest: "3.25%",
    previous: "3.50%",
    releaseDate: "2026-03-01",
    stale: false,
    series: [3.5, 3.5, 3.25, 3.25, 3.25, 3.25]
  },
  {
    code: "901Y009",
    name: "소비자물가지수",
    source: "KOSIS",
    latest: "114.2",
    previous: "113.8",
    releaseDate: "2026-02-28",
    stale: false,
    series: [112.9, 113.1, 113.4, 113.8, 114.0, 114.2]
  },
  {
    code: "FEDFUNDS",
    name: "미국 연방기금금리",
    source: "FRED",
    latest: "4.50%",
    previous: "4.75%",
    releaseDate: "2026-03-01",
    stale: false,
    series: [4.75, 4.75, 4.75, 4.5, 4.5, 4.5]
  }
] as const;

export const marketRows = [
  {
    symbol: "KRW=X",
    name: "USD/KRW",
    className: "외환",
    value: "1,372.5",
    change: "+0.62%",
    source: "Yahoo Finance",
    series: [1358, 1360, 1363, 1367, 1370, 1372]
  },
  {
    symbol: "^KS11",
    name: "KOSPI",
    className: "주식",
    value: "2,725.4",
    change: "-0.31%",
    source: "Investing.com",
    series: [2752, 2740, 2731, 2728, 2727, 2725]
  },
  {
    symbol: "CL=F",
    name: "WTI 원유",
    className: "원자재",
    value: "82.1",
    change: "+1.24%",
    source: "Seeking Alpha",
    series: [78.4, 79.2, 79.6, 80.4, 81.3, 82.1]
  }
] as const;

export const snapshots = [
  {
    id: "snapshot-1",
    project_id: "project-1",
    title: "USD/KRW 일봉 캡처",
    source_title: "Yahoo Finance USD/KRW",
    image_url: "https://placehold.co/1200x675/png?text=USD%2FKRW+Snapshot",
    preview_url: "https://placehold.co/1200x675/png?text=USD%2FKRW+Snapshot",
    source_url: "https://finance.yahoo.com/quote/KRW=X",
    captured_at: "2026-03-20 10:18",
    capture_mode: "stub",
    integration_boundary_note: "실제 브라우저 캡처는 아직 연결되지 않았습니다. 현재는 stub 썸네일과 메타데이터만 저장합니다.",
    note: "환율 급등 구간 표시",
    attached_evidences: [
      {
        evidence_id: "snapshot-evidence-1",
        source_kind: "snapshot",
        label: "USD/KRW 캡처 근거",
        source: {
          source_name: "Mock Snapshot",
          source_url: "https://finance.yahoo.com/quote/KRW=X",
          note: "환율 급등 구간 표시"
        }
      }
    ]
  },
  {
    id: "snapshot-2",
    project_id: "project-2",
    title: "국제유가 페이지 캡처",
    source_title: "Investing.com WTI",
    image_url: "https://placehold.co/1200x675/png?text=WTI+Snapshot",
    preview_url: "https://placehold.co/1200x675/png?text=WTI+Snapshot",
    source_url: "https://www.investing.com/commodities/crude-oil",
    captured_at: "2026-03-20 09:46",
    capture_mode: "stub",
    integration_boundary_note: "실제 브라우저 캡처는 아직 연결되지 않았습니다. 현재는 stub 썸네일과 메타데이터만 저장합니다.",
    note: "중동 리스크 문맥 참고",
    attached_evidences: [
      {
        evidence_id: "snapshot-evidence-2",
        source_kind: "snapshot",
        label: "국제유가 화면 캡처",
        source: {
          source_name: "Mock Snapshot",
          source_url: "https://www.investing.com/commodities/crude-oil",
          note: "중동 리스크 문맥 참고"
        }
      }
    ]
  }
] as const;

export const scriptSections = [
  {
    heading: "도입",
    content: "오늘은 금리 인하 기대가 왜 환율과 자금 흐름을 동시에 흔드는지 확인합니다.",
    evidences: ["ECOS 기준금리", "Yahoo Finance USD/KRW"]
  },
  {
    heading: "본론",
    content: "공식 통계에서는 정책금리 변화 방향을 확인하고, 시장 데이터에서는 즉각적인 가격 반응을 읽어야 합니다.",
    evidences: ["FRED 연방기금금리", "KOSIS 소비자물가지수"]
  },
  {
    heading: "결론",
    content: "숫자 자체보다 발표 시점과 전월 대비 방향을 함께 보는 것이 콘텐츠 신뢰도를 높입니다.",
    evidences: ["OECD 경기선행지수"]
  }
] as const;

export const scenes = [
  {
    title: "오프닝",
    description: "앵커가 환율 급등 화면 앞에서 핵심 질문을 제시합니다.",
    prompt: "한국 경제 앵커, 세로형 인포그래픽, 환율 상승 화살표, 한국어 자막",
    motion: "천천히 줌 인, 숫자 하이라이트"
  },
  {
    title: "공식 통계 설명",
    description: "기준금리와 물가 지표를 두 패널로 비교합니다.",
    prompt: "네이비 스튜디오, 기준금리와 CPI 인포그래픽, 동일 캐릭터 유지",
    motion: "패널 슬라이드, 지표별 카운트업"
  },
  {
    title: "시장 반응 정리",
    description: "환율과 증시를 연결한 흐름도를 보여줍니다.",
    prompt: "USD/KRW 차트, KOSPI 흐름선, 앵커 포인팅 장면",
    motion: "카메라 패닝, 차트 라인 드로우"
  }
] as const;

export const jobLogs = [
  { type: "대본 생성", status: "성공", startedAt: "10:12", note: "클로드 초안 생성 완료" },
  { type: "이미지 생성", status: "실행 중", startedAt: "10:18", note: "장면 2 재생성 진행 중" },
  { type: "영상 준비", status: "대기", startedAt: "10:19", note: "번들 생성 대기" },
  { type: "통계 검증", status: "실패", startedAt: "09:40", note: "공식 지표 매핑 충돌로 사용자 확인 필요" }
] as const;

export const evidenceItems = [
  {
    title: "ECOS 기준금리",
    detail: "2026-03-01 발표, 3.25%, 공식 통계",
    tone: "verified"
  },
  {
    title: "KOSIS 소비자물가지수",
    detail: "2026-02-28 발표, 114.2, 공식 통계",
    tone: "verified"
  },
  {
    title: "Yahoo Finance USD/KRW",
    detail: "보조 시각 참고 자료, 스크립트 수치 직접 인용 금지",
    tone: "supplementary"
  }
] as const;

export const filterPresets = {
  issueCategories: ["전체", "경제", "투자", "지정학"],
  dataFreshness: ["전체", "최신", "경고"],
  jobStatuses: ["전체", "대기", "실행 중", "성공", "실패"],
  periods: ["오늘", "최근 7일", "최근 30일"]
} as const;

export const settingsSections = [
  {
    tab: "API",
    title: "모델 및 외부 API",
    fields: [
      { key: "claude_model", label: "클로드 모델", value: "claude-sonnet", placeholder: "모델 이름" },
      { key: "claude_api_key", label: "Claude API 키", value: "", placeholder: "비밀 키 입력" },
      { key: "ecos_api_key", label: "ECOS API 키", value: "", placeholder: "비밀 키 입력" },
      { key: "fred_api_key", label: "FRED API 키", value: "", placeholder: "비밀 키 입력" }
    ]
  },
  {
    tab: "데이터",
    title: "검증 및 기본 범위",
    fields: [
      { key: "freshness_days", label: "신선도 기준(일)", value: "45", placeholder: "예: 45" },
      { key: "default_range", label: "기본 조회 기간(일)", value: "365", placeholder: "예: 365" },
      { key: "kosis_config", label: "KOSIS 설정", value: "기본 프로필", placeholder: "설정 이름" },
      { key: "oecd_config", label: "OECD 설정", value: "기본 프로필", placeholder: "설정 이름" }
    ]
  },
  {
    tab: "저장소",
    title: "출력 및 저장 경로",
    fields: [
      { key: "storage_mode", label: "저장소 모드", value: "local", placeholder: "local 또는 s3" },
      { key: "storage_root", label: "로컬 저장 경로", value: "./storage", placeholder: "경로 입력" },
      { key: "export_root", label: "출력 디렉터리", value: "./exports", placeholder: "경로 입력" },
      { key: "prompt_preset", label: "기본 프롬프트 프리셋", value: "설명형", placeholder: "프리셋 이름" }
    ]
  }
] as const;

export const dashboardTabs = ["오늘", "이번 주", "프로젝트별"] as const;
