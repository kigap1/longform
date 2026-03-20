import type {
  CreateProjectPayload,
  DashboardSnapshot,
  IssueArticleViewModel,
  IssueCardViewModel,
  IssueDiscoverySnapshot,
  IssueGroupViewModel,
  JobLogItem,
  JobsSnapshot,
  ProjectOption,
  WorkspaceSearchResult
} from "@/lib/api/types";
import { dashboardTabs, evidenceItems, filterPresets, marketRows, statisticsRows } from "@/lib/mock-data";


type StoredMockProject = ProjectOption & {
  issueFocus?: string;
};

type StoredMockJob = JobLogItem & {
  projectId: string;
};

type StoredIssueConfig = {
  keywords: string[];
  userInstructions: string;
  lastCollectedAt: string;
  runCount: number;
};

type StoredMockState = {
  version: number;
  projects: StoredMockProject[];
  jobs: StoredMockJob[];
  issueConfigsByProject: Record<string, StoredIssueConfig>;
};

type IssueCategory = "경제" | "투자" | "지정학";

type SeedTheme = {
  id: string;
  title: string;
  category: IssueCategory;
  summary: string;
  whyNow: string;
  youtubeAngles: string[];
  keywords: string[];
  regions: string[];
  marketImpact: number;
};

type SeedArticle = {
  id: string;
  themeId: string;
  title: string;
  sourceName: string;
  publishedAt: string;
  url: string;
  summary: string;
  country: string;
  region: string;
  popularity: number;
  credibility: number;
  keywords: string[];
};

const STORAGE_KEY = "factstudio.mock.studio.v4";
const STORAGE_VERSION = 4;

const DEFAULT_PROJECTS: StoredMockProject[] = [
  {
    id: "project-1",
    name: "미국 금리와 원화 변동성",
    summary: "금리, 환율, 외국인 수급을 함께 추적하는 메인 프로젝트",
    stage: "이슈 탐색",
    updatedAt: "2026-03-20 10:28",
    issueFocus: "금리, 환율, 외국인 수급"
  },
  {
    id: "project-2",
    name: "중동 리스크와 국제유가",
    summary: "유가와 물류 리스크를 중심으로 지정학 이슈를 추적",
    stage: "통계 검증",
    updatedAt: "2026-03-20 09:52",
    issueFocus: "중동, 유가, 공급망"
  },
  {
    id: "project-3",
    name: "중국 경기 둔화와 한국 수출",
    summary: "수출주, 경기선행지수, 중국 경기 지표를 연결",
    stage: "이미지 생성",
    updatedAt: "2026-03-19 18:10",
    issueFocus: "중국 경기, 한국 수출, 반도체"
  }
];

const DEFAULT_THEME_ORDER = ["fed-krw", "middle-east-oil", "china-export", "us-yields-tech", "japan-yen"];

const THEMES: readonly SeedTheme[] = [
  {
    id: "fed-krw",
    title: "미국 금리 인하 기대와 원화 약세 압력",
    category: "경제",
    summary: "연준 인하 기대가 달러, 원화, 외국인 수급에 동시에 영향을 주는 흐름을 다룹니다.",
    whyNow: "FOMC 기대와 환율 반응이 동시에 움직여 국내 시청자가 체감하기 좋은 주제입니다.",
    youtubeAngles: ["원달러 환율이 왜 다시 뛰는가", "연준 금리 기대가 한국 증시에 주는 영향", "외국인 수급과 환율을 같이 봐야 하는 이유"],
    keywords: ["금리", "환율", "원화", "달러", "연준", "fomc", "fed", "foreign", "외국인", "usd/krw"],
    regions: ["한국", "미국"],
    marketImpact: 0.94
  },
  {
    id: "middle-east-oil",
    title: "중동 리스크와 국제유가 재상승",
    category: "지정학",
    summary: "중동 긴장과 해상 물류 불안이 원유 가격, 운임, 인플레이션 경로에 미치는 영향을 정리합니다.",
    whyNow: "지정학과 물가를 한 번에 설명할 수 있어 경제 채널에서 반응이 좋은 주제입니다.",
    youtubeAngles: ["유가가 다시 오르면 한국 경제에 어떤 일이 생길까", "중동 리스크가 물가를 자극하는 경로", "해상 운임과 원유 가격을 같이 봐야 하는 이유"],
    keywords: ["유가", "중동", "원유", "해상", "운임", "공급망", "oil", "shipping", "brent", "wti"],
    regions: ["글로벌", "미국", "한국"],
    marketImpact: 0.9
  },
  {
    id: "china-export",
    title: "중국 경기 부양 기대와 한국 수출주의 온도차",
    category: "투자",
    summary: "중국 경기 둔화와 부양책 기대가 한국 수출, 반도체, 화학 업종에 미치는 영향을 다룹니다.",
    whyNow: "한국 주식 투자자와 경기 민감 업종 시청자 모두에게 설명 포인트가 분명합니다.",
    youtubeAngles: ["중국 경기 기대만으로 한국 수출주가 오를까", "반도체와 화학주는 중국을 얼마나 타는가", "중국 부양책 뉴스가 나올 때 확인할 숫자"],
    keywords: ["중국", "수출", "반도체", "부양", "중국 경기", "property", "stimulus", "export", "semiconductor"],
    regions: ["한국", "중국", "미국"],
    marketImpact: 0.84
  },
  {
    id: "us-yields-tech",
    title: "미국 장기금리와 기술주 밸류에이션 부담",
    category: "투자",
    summary: "미국 장기 국채금리의 재상승이 성장주와 AI 관련 종목의 밸류에이션에 주는 부담을 설명합니다.",
    whyNow: "나스닥과 국내 AI 관련주를 연결해서 설명하기 좋은 시기입니다.",
    youtubeAngles: ["미국 10년물이 오르면 성장주는 왜 흔들릴까", "AI 주도주와 금리의 미묘한 관계", "나스닥 변동성을 한국 투자자가 읽는 법"],
    keywords: ["장기금리", "채권", "기술주", "나스닥", "미국채", "10년물", "yield", "treasury", "ai"],
    regions: ["미국", "한국"],
    marketImpact: 0.82
  },
  {
    id: "japan-yen",
    title: "엔화 반등과 아시아 외환시장 재편",
    category: "경제",
    summary: "엔화 강세와 일본 통화정책 변화가 원화, 달러, 수출기업 가격 경쟁력에 미치는 파급을 봅니다.",
    whyNow: "원화와 함께 비교하면 아시아 통화 흐름을 쉽게 설명할 수 있습니다.",
    youtubeAngles: ["엔화가 오르면 원화는 어떻게 움직일까", "일본 정책 변화가 한국 수출에 주는 힌트", "아시아 외환시장에서 지금 봐야 할 통화 3가지"],
    keywords: ["엔화", "일본", "boj", "yen", "외환", "통화", "원엔", "japan"],
    regions: ["일본", "한국", "미국"],
    marketImpact: 0.76
  }
];

const NEWS_ARTICLES: readonly SeedArticle[] = [
  createSeedArticle("kr-1", "fed-krw", "미국 금리 인하 기대에 원화 약세 압력 커져", "연합뉴스", 2, "한국", 92, 0.91, ["금리", "원화", "환율", "연준"]),
  createSeedArticle("kr-2", "fed-krw", "원·달러 환율 1370원대 재진입, 외국인 수급도 흔들", "한국경제", 4, "한국", 89, 0.84, ["환율", "외국인", "증시", "원화"]),
  createSeedArticle("us-1", "fed-krw", "Fed cut hopes pressure the dollar outlook in Asia", "Reuters", 3, "미국", 95, 0.94, ["fed", "dollar", "asia", "fx"]),
  createSeedArticle("us-2", "fed-krw", "FOMC 기대감에 아시아 통화 변동성 확대", "Bloomberg", 6, "미국", 90, 0.9, ["fomc", "통화", "환율", "asia"]),
  createSeedArticle("kr-3", "middle-east-oil", "중동 긴장에 국제유가 상승, 국내 물가 자극 우려", "매일경제", 5, "한국", 86, 0.83, ["중동", "유가", "물가", "원유"]),
  createSeedArticle("us-3", "middle-east-oil", "Oil climbs as shipping concerns return to the Red Sea", "Reuters", 2, "미국", 96, 0.94, ["oil", "shipping", "red sea", "middle east"]),
  createSeedArticle("gl-1", "middle-east-oil", "해상 물류 리스크 재부각, 원유와 운임 동반 강세", "Financial Times", 7, "글로벌", 84, 0.87, ["해상", "물류", "운임", "공급망"]),
  createSeedArticle("kr-4", "middle-east-oil", "정유·항공 업종, 국제유가 반등에 엇갈린 주가 흐름", "서울경제", 8, "한국", 78, 0.8, ["정유", "항공", "국제유가", "주가"]),
  createSeedArticle("kr-5", "china-export", "중국 경기 부양 기대에도 한국 수출주는 선별 대응", "조선비즈", 3, "한국", 83, 0.81, ["중국", "수출", "반도체", "부양"]),
  createSeedArticle("gl-2", "china-export", "China stimulus hopes lift selective Asian exporters", "WSJ", 9, "미국", 82, 0.86, ["china", "stimulus", "exporters", "asia"]),
  createSeedArticle("kr-6", "china-export", "반도체와 화학, 중국 수요 회복 기대에 온도차", "이데일리", 6, "한국", 79, 0.78, ["반도체", "화학", "중국 수요"]),
  createSeedArticle("us-4", "china-export", "Property weakness still clouds Korea export rebound", "Reuters", 10, "미국", 80, 0.92, ["property", "korea export", "china"]),
  createSeedArticle("us-5", "us-yields-tech", "US 10-year yield rise revives valuation pressure on tech", "Bloomberg", 4, "미국", 88, 0.9, ["10-year", "yield", "tech", "valuation"]),
  createSeedArticle("kr-7", "us-yields-tech", "미 장기금리 오름세에 국내 AI주 변동성 확대", "한경닷컴", 9, "한국", 76, 0.77, ["장기금리", "ai", "기술주", "변동성"]),
  createSeedArticle("us-6", "us-yields-tech", "Treasury yields challenge growth stock leadership", "Seeking Alpha", 12, "미국", 74, 0.75, ["treasury", "growth", "stocks", "yield"]),
  createSeedArticle("jp-1", "japan-yen", "엔화 반등에 아시아 통화시장 긴장 재점화", "니혼게이자이", 11, "일본", 71, 0.82, ["엔화", "boj", "아시아 통화"]),
  createSeedArticle("kr-8", "japan-yen", "원·엔 환율 상승, 수입물가와 여행수지에 미묘한 영향", "연합인포맥스", 13, "한국", 69, 0.84, ["원엔", "환율", "수입물가"]),
  createSeedArticle("us-7", "japan-yen", "BOJ shift ripples through regional FX markets", "Reuters", 14, "미국", 77, 0.93, ["boj", "fx", "yen", "asia"]),
  createSeedArticle("kr-9", "fed-krw", "미국 CPI 둔화 기대와 한국은행 고민 사이의 환율", "머니투데이", 14, "한국", 74, 0.79, ["cpi", "한국은행", "환율", "미국 물가"]),
  createSeedArticle("gl-3", "middle-east-oil", "Brent and shipping insurance costs rise together", "Bloomberg", 15, "글로벌", 72, 0.89, ["brent", "shipping insurance", "oil"]),
  createSeedArticle("kr-10", "china-export", "중국 부동산 부진이 한국 철강·화학에 남긴 숙제", "매일경제", 16, "한국", 68, 0.8, ["중국 부동산", "철강", "화학"]),
  createSeedArticle("us-8", "fed-krw", "Asian FX traders brace for a softer Fed path", "WSJ", 18, "미국", 70, 0.85, ["fed", "asian fx", "달러"]),
  createSeedArticle("kr-11", "us-yields-tech", "나스닥 흔들릴 때 한국 성장주도 같이 흔들리는 이유", "서울경제", 18, "한국", 67, 0.79, ["나스닥", "성장주", "금리"]),
  createSeedArticle("kr-12", "middle-east-oil", "국제유가 반등이 국내 물가 기대심리 자극", "한국경제TV", 20, "한국", 66, 0.76, ["유가", "물가", "기대심리"])
];

let cachedState: StoredMockState | null = null;

export function listMockProjects(): ProjectOption[] {
  return readState().projects.map((project) => ({ ...project }));
}

export function createMockProject(payload: CreateProjectPayload): ProjectOption {
  const state = readState();
  const now = formatLocalTimestamp(new Date());
  const created: StoredMockProject = {
    id: `project-${Math.random().toString(36).slice(2, 10)}`,
    name: payload.name.trim(),
    summary: payload.description?.trim() || "새로 만든 콘텐츠 프로젝트",
    stage: "이슈 탐색",
    updatedAt: now,
    issueFocus: payload.issue_focus?.trim() || payload.name.trim()
  };

  state.projects = [created, ...state.projects];
  state.issueConfigsByProject[created.id] = {
    keywords: tokenize(payload.issue_focus || payload.name),
    userInstructions: "",
    lastCollectedAt: now,
    runCount: 0
  };
  state.jobs.unshift({
    projectId: created.id,
    type: "프로젝트 생성",
    status: "성공",
    startedAt: now,
    note: `${created.name} 프로젝트가 생성되었습니다.`
  });
  saveState(state);
  return { ...created };
}

export function getMockIssueDiscoverySnapshot(projectId?: string): IssueDiscoverySnapshot {
  const state = readState();
  const project = resolveProject(state, projectId);
  const issueConfig = resolveIssueConfig(state, project);
  return buildIssueSnapshot(project, issueConfig);
}

export function rankMockIssues(payload: {
  project_id?: string;
  keywords?: readonly string[];
  user_instructions?: string;
}): IssueDiscoverySnapshot {
  const state = readState();
  const project = resolveProject(state, payload.project_id);
  const now = formatLocalTimestamp(new Date());
  const nextConfig: StoredIssueConfig = {
    keywords: payload.keywords?.length ? [...payload.keywords] : resolveIssueConfig(state, project).keywords,
    userInstructions: payload.user_instructions?.trim() ?? resolveIssueConfig(state, project).userInstructions,
    lastCollectedAt: now,
    runCount: resolveIssueConfig(state, project).runCount + 1
  };
  state.issueConfigsByProject[project.id] = nextConfig;
  project.updatedAt = now;
  project.stage = "이슈 탐색";
  state.jobs.unshift({
    projectId: project.id,
    type: "기사 수집",
    status: "성공",
    startedAt: now,
    note: buildIssueJobNote(nextConfig.keywords, nextConfig.userInstructions)
  });
  saveState(state);
  return buildIssueSnapshot(project, nextConfig);
}

export function getMockDashboardSnapshot(projectId?: string): DashboardSnapshot {
  const state = readState();
  const snapshot = getMockIssueDiscoverySnapshot(projectId);
  const jobs = getMockJobsSnapshot(projectId);
  const successJobs = jobs.items.filter((item) => item.status === "성공").length;
  const runningJobs = jobs.items.filter((item) => item.status === "실행 중").length;
  const pendingJobs = jobs.items.filter((item) => item.status === "대기").length;
  const failedJobs = jobs.items.filter((item) => item.status === "실패").length;

  return {
    metrics: [
      { label: "활성 프로젝트", value: String(state.projects.length), change: `현재 ${state.projects.length}개` },
      { label: "검증 완료 근거", value: String(evidenceItems.filter((item) => item.tone === "verified").length), change: `전체 ${evidenceItems.length}` },
      { label: "대기 작업", value: String(pendingJobs + runningJobs), change: `실행 중 ${runningJobs}` },
      { label: "완료 산출물", value: String(successJobs), change: `실패 ${failedJobs}` }
    ],
    tabs: dashboardTabs,
    issues: snapshot.items.slice(0, 3),
    evidences: evidenceItems.slice(0, 4),
    jobs: jobs.items.slice(0, 5)
  };
}

export function getMockJobsSnapshot(projectId?: string): JobsSnapshot {
  const state = readState();
  const project = resolveProject(state, projectId);
  const items = state.jobs.filter((item) => item.projectId === project.id).map((item) => ({ ...item }));
  const counts = {
    default: items.filter((item) => item.status === "대기").length,
    warning: items.filter((item) => item.status === "실행 중").length,
    success: items.filter((item) => item.status === "성공").length,
    danger: items.filter((item) => item.status === "실패").length
  };

  return {
    statuses: filterPresets.jobStatuses,
    summary: [
      { label: "대기", value: String(counts.default), tone: "default" as const },
      { label: "실행 중", value: String(counts.warning), tone: "warning" as const },
      { label: "성공", value: String(counts.success), tone: "success" as const },
      { label: "실패", value: String(counts.danger), tone: "danger" as const }
    ],
    items
  };
}

export function searchMockWorkspace(projectId: string | undefined, query: string): WorkspaceSearchResult[] {
  const trimmed = query.trim();
  if (trimmed.length < 2) return [];

  const projects = listMockProjects()
    .filter((project) => matchesText(trimmed, [project.name, project.summary, project.issueFocus ?? ""]))
    .slice(0, 2)
    .map((project) => ({
      id: `project-${project.id}`,
      kind: "프로젝트" as const,
      title: project.name,
      detail: project.summary,
      href: "/dashboard"
    }));

  const issues = getMockIssueDiscoverySnapshot(projectId).items
    .filter((issue) => matchesText(trimmed, [issue.title, issue.summary, issue.whyNow, ...issue.youtubeAngles]))
    .slice(0, 4)
    .map((issue) => ({
      id: `issue-${issue.id}`,
      kind: "이슈" as const,
      title: issue.title,
      detail: `${issue.category} · 기사 ${issue.articleCount}건`,
      href: "/issues"
    }));

  const statistics = statisticsRows
    .filter((row) => matchesText(trimmed, [row.code, row.name, row.source]))
    .slice(0, 3)
    .map((row) => ({
      id: `stat-${row.code}`,
      kind: "지표" as const,
      title: row.name,
      detail: `${row.source} · ${row.latest}`,
      href: "/statistics"
    }));

  const markets = marketRows
    .filter((row) => matchesText(trimmed, [row.symbol, row.name, row.className, row.source]))
    .slice(0, 3)
    .map((row) => ({
      id: `market-${row.symbol}`,
      kind: "자산" as const,
      title: row.name,
      detail: `${row.symbol} · ${row.value}`,
      href: "/market"
    }));

  return [...projects, ...issues, ...statistics, ...markets].slice(0, 8);
}

function readState(): StoredMockState {
  if (cachedState) {
    return cachedState;
  }

  if (typeof window === "undefined") {
    cachedState = createInitialState();
    return cachedState;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    cachedState = createInitialState();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cachedState));
    return cachedState;
  }

  try {
    const parsed = JSON.parse(raw) as StoredMockState;
    if (parsed.version !== STORAGE_VERSION) {
      cachedState = createInitialState();
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cachedState));
      return cachedState;
    }
    cachedState = parsed;
    return cachedState;
  } catch {
    cachedState = createInitialState();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cachedState));
    return cachedState;
  }
}

function saveState(state: StoredMockState) {
  cachedState = state;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }
}

function createInitialState(): StoredMockState {
  const issueConfigsByProject: Record<string, StoredIssueConfig> = {};
  DEFAULT_PROJECTS.forEach((project) => {
    issueConfigsByProject[project.id] = {
      keywords: tokenize(project.issueFocus || project.name),
      userInstructions: "",
      lastCollectedAt: project.updatedAt,
      runCount: 0
    };
  });

  return {
    version: STORAGE_VERSION,
    projects: DEFAULT_PROJECTS.map((project) => ({ ...project })),
    jobs: [
      { projectId: "project-1", type: "기사 수집", status: "성공", startedAt: "2026-03-20 10:28", note: "금리, 환율 키워드 기반으로 이슈 4건을 갱신했습니다." },
      { projectId: "project-1", type: "대본 생성", status: "성공", startedAt: "2026-03-20 10:12", note: "클로드 초안 생성 완료" },
      { projectId: "project-2", type: "기사 수집", status: "성공", startedAt: "2026-03-20 09:52", note: "중동, 유가 키워드 기반으로 이슈 3건을 갱신했습니다." },
      { projectId: "project-3", type: "기사 수집", status: "성공", startedAt: "2026-03-19 18:10", note: "중국, 수출 키워드 기반으로 이슈 3건을 갱신했습니다." }
    ],
    issueConfigsByProject
  };
}

function resolveProject(state: StoredMockState, projectId?: string): StoredMockProject {
  return state.projects.find((project) => project.id === projectId) ?? state.projects[0];
}

function resolveIssueConfig(state: StoredMockState, project: StoredMockProject): StoredIssueConfig {
  return (
    state.issueConfigsByProject[project.id] ?? {
      keywords: tokenize(project.issueFocus || project.name),
      userInstructions: "",
      lastCollectedAt: project.updatedAt,
      runCount: 0
    }
  );
}

function buildIssueSnapshot(project: StoredMockProject, issueConfig: StoredIssueConfig): IssueDiscoverySnapshot {
  const baseTokens = tokenize(project.name, project.summary, project.issueFocus || "");
  const keywordTokens = tokenize(...issueConfig.keywords);
  const instructionTokens = tokenize(issueConfig.userInstructions);
  const requestedCountry = inferCountryPreference([...keywordTokens, ...instructionTokens]);

  const rankedThemes = THEMES.map((theme) => {
    const keywordScore = tokenOverlap(theme.keywords, keywordTokens) * 0.42;
    const projectScore = tokenOverlap(theme.keywords, baseTokens) * 0.24;
    const instructionScore = tokenOverlap(theme.keywords, instructionTokens) * 0.16;
    const regionBoost = requestedCountry && theme.regions.includes(requestedCountry) ? 0.08 : 0;
    return {
      theme,
      relevance: keywordScore + projectScore + instructionScore + regionBoost
    };
  }).sort((left, right) => right.relevance - left.relevance);

  const chosenThemes = rankedThemes.filter((item) => item.relevance > 0).slice(0, 5);
  const activeThemes = chosenThemes.length ? chosenThemes : rankedThemes.filter((item) => DEFAULT_THEME_ORDER.includes(item.theme.id)).slice(0, 4);

  const items = activeThemes
    .map(({ theme, relevance }) => {
      const articles = NEWS_ARTICLES
        .filter((article) => article.themeId === theme.id)
        .filter((article) => !requestedCountry || article.country === requestedCountry || article.country === "글로벌")
        .sort((left, right) => {
          const leftPopularity = left.popularity + articleCycleBoost(left.id, issueConfig.runCount);
          const rightPopularity = right.popularity + articleCycleBoost(right.id, issueConfig.runCount);
          return rightPopularity - leftPopularity;
        });
      const regions = unique(articles.map((article) => article.country));
      const topSources = unique(articles.map((article) => article.sourceName)).slice(0, 4);
      const averagePopularity = articles.reduce((sum, article) => sum + article.popularity, 0) / Math.max(articles.length, 1);
      const averageCredibility = articles.reduce((sum, article) => sum + article.credibility, 0) / Math.max(articles.length, 1);
      const recencyScore = computeRecencyScore(articles);
      const score = Math.min(
        0.99,
        Number(
          (
            recencyScore * 0.22 +
            Math.min(articles.length / 6, 1) * 0.18 +
            averageCredibility * 0.2 +
            (averagePopularity / 100) * 0.18 +
            theme.marketImpact * 0.17 +
            Math.min(relevance, 1) * 0.05 +
            ((issueConfig.runCount + DEFAULT_THEME_ORDER.indexOf(theme.id)) % 3) * 0.01
          ).toFixed(2)
        )
      );

      return {
        id: theme.id,
        title: theme.title,
        category: theme.category,
        score,
        reasons: buildReasons(theme, articles, requestedCountry),
        summary: theme.summary,
        articleCount: articles.length,
        regions,
        topSources,
        youtubeAngles: theme.youtubeAngles,
        whyNow: theme.whyNow,
        articles: articles.map(toIssueArticle)
      } satisfies IssueCardViewModel;
    })
    .sort((left, right) => right.score - left.score);

  const groups = items.map((issue) => ({
    issueId: issue.id,
    title: `${issue.title} 기사 ${issue.articleCount}건`,
    detail: `${issue.regions.join(", ")} 기사에서 공통 키워드가 모였습니다.`,
    articleCount: issue.articleCount,
    regions: issue.regions,
    topSources: issue.topSources,
    articles: issue.articles
  })) satisfies IssueGroupViewModel[];

  const highlights = items.slice(0, 3).map((issue, index) => ({
    issueId: issue.id,
    title: issue.title,
    subtitle:
      index === 0
        ? `지금 가장 강한 주제 · ${issue.articleCount}건`
        : index === 1
          ? `시장 연결성이 높은 주제 · ${issue.regions.join("/")}`
          : `유튜브 확장성이 좋은 주제 · ${issue.youtubeAngles[0] ?? issue.summary}`,
    tone: index === 0 ? "hot" : index === 1 ? "watch" : "idea"
  })) satisfies IssueDiscoverySnapshot["highlights"];

  return {
    filters: filterPresets.issueCategories,
    regionFilters: ["전체", ...unique(items.flatMap((item) => item.regions))],
    sortOptions: ["우선순위", "최신성", "기사 수", "인기순"],
    keywordSuggestions: unique(THEMES.flatMap((theme) => theme.keywords)).slice(0, 12),
    highlights,
    lastCollectedAt: issueConfig.lastCollectedAt,
    items,
    groups
  };
}

function buildReasons(theme: SeedTheme, articles: SeedArticle[], requestedCountry: string | null): string[] {
  const reasons = [
    articles.length >= 4 ? "관련 기사 빈도가 높음" : "핵심 기사 묶음이 선명함",
    theme.marketImpact >= 0.88 ? "시장 영향도가 높음" : "투자/경기 연결 설명이 쉬움"
  ];
  if (requestedCountry && articles.some((article) => article.country === requestedCountry)) {
    reasons.push(`${requestedCountry} 기사 비중을 반영함`);
  }
  if (articles.some((article) => article.popularity >= 90)) {
    reasons.push("인기 기사 다수가 포함됨");
  }
  return reasons;
}

function toIssueArticle(article: SeedArticle): IssueArticleViewModel {
  return {
    id: article.id,
    title: article.title,
    sourceName: article.sourceName,
    publishedAt: article.publishedAt,
    url: article.url,
    summary: article.summary,
    country: article.country,
    region: article.region,
    popularity: article.popularity,
    credibility: article.credibility
  };
}

function buildIssueJobNote(keywords: readonly string[], userInstructions: string) {
  const keywordPart = keywords.length ? `${keywords.join(", ")} 키워드 기반으로` : "프로젝트 기본 주제를 바탕으로";
  const instructionPart = userInstructions.trim() ? " 지시문을 반영해" : "";
  return `${keywordPart}${instructionPart} 이슈를 다시 계산했습니다.`;
}

function createSeedArticle(
  id: string,
  themeId: string,
  title: string,
  sourceName: string,
  hoursAgo: number,
  country: string,
  popularity: number,
  credibility: number,
  keywords: string[]
): SeedArticle {
  const publishedAt = new Date(Date.now() - hoursAgo * 60 * 60 * 1000);
  return {
    id,
    themeId,
    title,
    sourceName,
    publishedAt: formatLocalTimestamp(publishedAt),
    url: buildNewsSearchUrl(title, sourceName),
    summary: `${title}에 대한 핵심 맥락을 요약한 모의 기사입니다.`,
    country,
    region: country === "한국" || country === "일본" || country === "중국" ? "아시아" : country === "미국" ? "북미" : "글로벌",
    popularity,
    credibility,
    keywords
  };
}

function tokenize(...values: string[]) {
  return unique(
    values
      .flatMap((value) =>
        value
          .split(/[,\n/|]/g)
          .flatMap((piece) => piece.split(/\s+/g))
          .map((piece) => piece.trim().toLowerCase())
          .filter((piece) => piece.length >= 2)
      )
  );
}

function tokenOverlap(themeKeywords: readonly string[], tokens: readonly string[]) {
  return themeKeywords.reduce((score, themeKeyword) => {
    if (tokens.some((token) => themeKeyword.toLowerCase().includes(token) || token.includes(themeKeyword.toLowerCase()))) {
      return score + 1;
    }
    return score;
  }, 0);
}

function unique<T>(values: readonly T[]) {
  return Array.from(new Set(values));
}

function computeRecencyScore(articles: readonly SeedArticle[]) {
  if (!articles.length) return 0.5;
  const latest = Math.max(...articles.map((article) => new Date(article.publishedAt.replace(" ", "T")).getTime()));
  const hours = Math.max(0, (Date.now() - latest) / (1000 * 60 * 60));
  return Math.max(0.2, 1 - hours / 48);
}

function articleCycleBoost(articleId: string, runCount: number) {
  const seed = articleId
    .split("")
    .reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return ((seed + runCount) % 5) * 2;
}

function inferCountryPreference(tokens: readonly string[]) {
  if (tokens.some((token) => ["한국", "국내", "korea", "kr"].includes(token))) return "한국";
  if (tokens.some((token) => ["미국", "usa", "us", "america"].includes(token))) return "미국";
  if (tokens.some((token) => ["중국", "china"].includes(token))) return "중국";
  if (tokens.some((token) => ["일본", "japan", "yen", "엔화"].includes(token))) return "일본";
  if (tokens.some((token) => ["글로벌", "global", "국제"].includes(token))) return "글로벌";
  return null;
}

function matchesText(query: string, values: readonly string[]) {
  const normalizedQuery = query.trim().toLowerCase();
  return values.some((value) => value.toLowerCase().includes(normalizedQuery));
}

function formatLocalTimestamp(value: Date) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  const hours = String(value.getHours()).padStart(2, "0");
  const minutes = String(value.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

function buildNewsSearchUrl(title: string, sourceName: string) {
  const query = encodeURIComponent(title);
  const source = sourceName.toLowerCase();

  if (source.includes("reuters")) {
    return `https://www.reuters.com/site-search/?query=${query}`;
  }
  if (source.includes("bloomberg")) {
    return `https://www.bloomberg.com/search?query=${query}`;
  }
  if (source.includes("wsj")) {
    return `https://www.wsj.com/search?query=${query}`;
  }
  if (source.includes("financial times")) {
    return `https://www.ft.com/search?q=${query}`;
  }
  if (source.includes("seeking alpha")) {
    return `https://seekingalpha.com/search?q=${query}`;
  }

  return `https://news.google.com/search?q=${encodeURIComponent(`${title} ${sourceName}`)}`;
}
