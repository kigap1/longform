import {
  captureSnapshot as captureSnapshotMock,
  getCharacterLibrary,
  getDashboardSnapshot,
  getImageWorkspace,
  getIssueDiscoverySnapshot,
  getJobsSnapshot,
  getMarketSnapshot,
  getProjects as getProjectsMock,
  getReviewWorkspace,
  getScriptWorkspace,
  getSettingsSnapshot as getSettingsSnapshotMock,
  getSnapshotLibrary,
  getStatisticsSnapshot as getStatisticsSnapshotMock,
  getVideoWorkspace
} from "@/lib/api/mock-api";
import { dashboardTabs, filterPresets } from "@/lib/mock-data";
import type {
  CharacterLibrarySnapshot,
  DashboardSnapshot,
  EvidencePanelItem,
  IssueCardViewModel,
  IssueDiscoverySnapshot,
  JobLogItem,
  JobsSnapshot,
  MarketSnapshot,
  ProjectOption,
  SettingUpsertPayload,
  SettingsSnapshot,
  SnapshotCapturePayload,
  SnapshotLibraryResponse,
  SnapshotSummary,
  StatisticsSnapshot
} from "@/lib/api/types";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API !== "false";
const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, "");
const SETTING_FIELD_META: Record<string, { label: string; placeholder: string }> = {
  claude_model: { label: "클로드 모델", placeholder: "모델 이름" },
  claude_api_key: { label: "Claude API 키", placeholder: "비밀 키 입력" },
  ecos_api_key: { label: "ECOS API 키", placeholder: "비밀 키 입력" },
  fred_api_key: { label: "FRED API 키", placeholder: "비밀 키 입력" },
  freshness_threshold_days: { label: "신선도 기준(일)", placeholder: "예: 45" },
  freshness_days: { label: "신선도 기준(일)", placeholder: "예: 45" },
  default_date_range_days: { label: "기본 조회 기간(일)", placeholder: "예: 365" },
  default_range: { label: "기본 조회 기간(일)", placeholder: "예: 365" },
  kosis_api_key: { label: "KOSIS API 키", placeholder: "비밀 키 입력" },
  oecd_api_key: { label: "OECD API 키", placeholder: "비밀 키 입력" },
  storage_mode: { label: "저장소 모드", placeholder: "local 또는 s3" },
  mode: { label: "저장소 모드", placeholder: "local 또는 s3" },
  local_storage_root: { label: "로컬 저장 경로", placeholder: "경로 입력" },
  storage_root: { label: "로컬 저장 경로", placeholder: "경로 입력" },
  export_root: { label: "출력 디렉터리", placeholder: "경로 입력" },
  prompt_preset: { label: "기본 프롬프트 프리셋", placeholder: "프리셋 이름" }
};

type RawProjectListResponse = {
  items: Array<{
    id: string;
    name: string;
    description: string;
    issue_focus?: string | null;
    updated_at: string;
  }>;
};

type RawIssueListResponse = {
  items: Array<{
    id: string;
    title: string;
    category: string;
    priority_score: number;
    reasons: string[];
    related_articles: Array<{
      id: string;
      title: string;
      source_name: string;
      published_at: string;
      url: string;
      summary: string;
    }>;
  }>;
};

type RawStatisticListResponse = {
  items: Array<{
    id: string;
    indicator_code: string;
    name: string;
    source_name: string;
    source_url: string;
    latest_value: number;
    previous_value?: number | null;
    release_date: string;
    unit: string;
    stale: boolean;
    series_preview: Array<{ date: string; value: number }>;
  }>;
};

type RawEvidenceContextResponse = {
  items: Array<{
    label: string;
    summary: string;
    source_kind: string;
    release_date?: string | null;
    value?: number | null;
    source: {
      source_name: string;
      source_url: string;
      note?: string | null;
    };
  }>;
};

type RawMarketSearchResponse = {
  items: Array<{
    symbol: string;
    display_name: string;
    asset_class: string;
    source_name: string;
    latest_value: number;
    change_percent: number;
    chart_points: Array<{ date: string; value: number }>;
  }>;
};

type RawCharacterListResponse = {
  items: Array<{
    id: string;
    name: string;
    description: string;
    style_rules: string[];
    locked: boolean;
  }>;
};

type RawAppSettingsResponse = {
  items: Array<{
    category: string;
    key: string;
    value: string;
    secret: boolean;
  }>;
};

type RawEvidenceReportResponse = {
  sections: Array<{
    title: string;
    summary: string;
    evidences: Array<{
      evidence_id: string;
      source_kind: string;
      label: string;
      release_date?: string | null;
      value?: number | null;
      source: {
        source_name: string;
        source_url: string;
        note?: string | null;
      };
    }>;
  }>;
};

type RawJobSummary = {
  id: string;
  job_type: string;
  status: string;
  project_id: string;
  created_at: string;
  updated_at: string;
};

type RawJobDetailResponse = {
  summary: RawJobSummary;
  logs: Array<{
    timestamp: string;
    level: string;
    message: string;
  }>;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`API 요청 실패: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function resolveApiUrl(path: string): string {
  if (!path) return path;
  if (/^(https?:)?\/\//.test(path) || path.startsWith("data:")) {
    return path;
  }
  if (path.startsWith("/")) {
    return `${API_ORIGIN}${path}`;
  }
  return path;
}

export const apiClient = {
  projects: async (): Promise<ProjectOption[]> => {
    if (USE_MOCK_API) return getProjectsMock();
    const response = await request<RawProjectListResponse>("/projects");
    return response.items.map((project) => ({
      id: project.id,
      name: project.name,
      summary: project.description || "프로젝트 설명이 아직 없습니다.",
      stage: "운영 중",
      updatedAt: formatDateTime(project.updated_at)
    }));
  },

  dashboard: async (projectId?: string): Promise<DashboardSnapshot> => {
    if (USE_MOCK_API) return getDashboardSnapshot();
    const [projects, issues, jobs, evidences] = await Promise.all([
      apiClient.projects(),
      apiClient.issues(projectId),
      apiClient.jobs(projectId),
      projectId ? fetchEvidenceReport(projectId) : Promise.resolve([] as EvidencePanelItem[])
    ]);

    const successJobs = jobs.items.filter((item) => item.status === "성공").length;
    const runningJobs = jobs.items.filter((item) => item.status === "실행 중").length;
    const pendingJobs = jobs.items.filter((item) => item.status === "대기").length;
    const failedJobs = jobs.items.filter((item) => item.status === "실패").length;
    const verifiedEvidenceCount = evidences.filter((item) => item.tone === "verified").length;

    return {
      metrics: [
        { label: "활성 프로젝트", value: String(projects.length), change: `운영 중 ${projects.length}` },
        { label: "검증 완료 근거", value: String(verifiedEvidenceCount), change: `전체 ${evidences.length}` },
        { label: "대기 작업", value: String(pendingJobs + runningJobs), change: `실행 중 ${runningJobs}` },
        { label: "완료 산출물", value: String(successJobs), change: `실패 ${failedJobs}` }
      ],
      tabs: dashboardTabs,
      issues: issues.items.slice(0, 3),
      evidences: evidences.slice(0, 4),
      jobs: jobs.items.slice(0, 5)
    };
  },

  issues: async (projectId?: string): Promise<IssueDiscoverySnapshot> => {
    if (USE_MOCK_API) return getIssueDiscoverySnapshot();
    const response = await request<RawIssueListResponse>(`/issues${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`);
    const items = response.items.map(toIssueCard);
    return {
      filters: filterPresets.issueCategories,
      items,
      groups: response.items.map((issue) => ({
        title: `${issue.title} 기사 ${issue.related_articles.length}건`,
        detail:
          issue.related_articles.length > 0
            ? `${unique(issue.related_articles.map((article) => article.source_name)).join(", ")} 기사 묶음`
            : "연결된 기사 없음"
      }))
    };
  },

  statistics: async (projectId: string): Promise<StatisticsSnapshot> => {
    if (USE_MOCK_API) return getStatisticsSnapshotMock();
    const issues = await request<RawIssueListResponse>(`/issues?project_id=${encodeURIComponent(projectId)}`);
    const issueId = issues.items[0]?.id ?? projectId;
    const statistics = await request<RawStatisticListResponse>("/stats/recommend", {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, issue_id: issueId })
    });
    const evidenceContext = await request<RawEvidenceContextResponse>("/stats/evidence-context", {
      method: "POST",
      body: JSON.stringify({
        project_id: projectId,
        indicator_codes: statistics.items.slice(0, 3).map((item) => item.indicator_code),
        market_symbols: []
      })
    });

    return {
      filters: filterPresets.dataFreshness,
      items: statistics.items.map((item) => ({
        code: item.indicator_code,
        name: item.name,
        source: item.source_name,
        latest: formatValue(item.latest_value, item.unit),
        previous: item.previous_value == null ? "-" : formatValue(item.previous_value, item.unit),
        releaseDate: item.release_date,
        stale: item.stale,
        series: item.series_preview.map((point) => point.value)
      })),
      evidences: evidenceContext.items.map((item) => ({
        title: item.label,
        detail: `${item.source.source_name} · ${item.summary}`,
        tone: item.source_kind === "market_data" ? "supplementary" : "verified"
      }))
    };
  },

  market: async (): Promise<MarketSnapshot> => {
    if (USE_MOCK_API) return getMarketSnapshot();
    const responses = await Promise.all([
      request<RawMarketSearchResponse>("/market/search", { method: "POST", body: JSON.stringify({ query: "KRW" }) }),
      request<RawMarketSearchResponse>("/market/search", { method: "POST", body: JSON.stringify({ query: "KOSPI" }) }),
      request<RawMarketSearchResponse>("/market/search", { method: "POST", body: JSON.stringify({ query: "WTI" }) })
    ]);

    const seen = new Set<string>();
    const items = responses
      .flatMap((response) => response.items)
      .filter((item) => {
        if (seen.has(item.symbol)) return false;
        seen.add(item.symbol);
        return true;
      })
      .slice(0, 6)
      .map((item) => ({
        symbol: item.symbol,
        name: item.display_name,
        className: translateAssetClass(item.asset_class),
        value: formatPlainNumber(item.latest_value),
        change: formatPercent(item.change_percent),
        source: item.source_name,
        series: item.chart_points.map((point) => point.value)
      }));

    return {
      periods: filterPresets.periods,
      items
    };
  },

  snapshots: (projectId?: string) =>
    USE_MOCK_API
      ? getSnapshotLibrary(projectId)
      : request<SnapshotLibraryResponse>(`/snapshot/list${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`),

  captureSnapshot: (payload: SnapshotCapturePayload) =>
    USE_MOCK_API
      ? captureSnapshotMock(payload)
      : request<SnapshotSummary>("/snapshot/capture", { method: "POST", body: JSON.stringify(payload) }),

  characters: async (projectId?: string): Promise<CharacterLibrarySnapshot> => {
    if (USE_MOCK_API) return getCharacterLibrary();
    const response = await request<RawCharacterListResponse>(
      `/characters${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`
    );
    return {
      items: response.items.map((item) => ({
        id: item.id,
        name: item.name,
        description: item.description,
        rules: item.style_rules,
        locked: item.locked
      }))
    };
  },

  generateScript: (payload: unknown) =>
    USE_MOCK_API ? getScriptWorkspace() : request("/scripts/generate", { method: "POST", body: JSON.stringify(payload) }),

  images: () => getImageWorkspace(),

  prepareVideos: (payload: unknown) =>
    USE_MOCK_API ? getVideoWorkspace() : request("/videos/prepare", { method: "POST", body: JSON.stringify(payload) }),

  review: () => getReviewWorkspace(),

  settings: async (): Promise<SettingsSnapshot> => {
    if (USE_MOCK_API) {
      const snapshot = await getSettingsSnapshotMock();
      return {
        tabs: snapshot.tabs,
        sections: snapshot.sections.map((section) => ({
          category: mockCategoryFromTab(section.tab),
          tab: section.tab,
          title: section.title,
          fields: section.fields.map((field) => ({
            category: mockCategoryFromTab(section.tab),
            key: field.key,
            label: field.label,
            value: field.value,
            placeholder: field.placeholder
          }))
        }))
      };
    }
    const response = await request<RawAppSettingsResponse>("/settings");
    const grouped = new Map<string, RawAppSettingsResponse["items"]>();
    response.items.forEach((item) => {
      const rows = grouped.get(item.category) ?? [];
      rows.push(item);
      grouped.set(item.category, rows);
    });

    const sections = Array.from(grouped.entries())
      .map(([category, items]) => {
        const tab = settingTab(category);
        return {
          category,
          tab,
          title: settingTitle(category),
          fields: items.map((field) => ({
            category,
            key: field.key,
            label: settingLabel(field.key),
            value: field.value,
            placeholder: settingPlaceholder(field.key),
            secret: field.secret
          }))
        };
      })
      .sort((left, right) => settingOrder(left.category) - settingOrder(right.category));

    return {
      tabs: unique(sections.map((section) => section.tab)),
      sections
    };
  },

  saveSettings: async (payloads: readonly SettingUpsertPayload[]): Promise<{ message: string }> => {
    if (USE_MOCK_API) {
      return { message: "mock settings saved" };
    }
    await Promise.all(
      payloads.map((payload) =>
        request<{ message: string }>("/settings", {
          method: "PUT",
          body: JSON.stringify(payload)
        })
      )
    );
    return { message: "설정이 저장되었습니다." };
  },

  jobs: async (projectId?: string): Promise<JobsSnapshot> => {
    if (USE_MOCK_API) return getJobsSnapshot();
    const summaries = await request<RawJobSummary[]>(`/jobs${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`);
    const details = await Promise.all(
      summaries.map((summary) => request<RawJobDetailResponse>(`/jobs/${encodeURIComponent(summary.id)}`))
    );
    const items = details.map((detail) => ({
      id: detail.summary.id,
      type: translateJobType(detail.summary.job_type),
      status: translateJobStatus(detail.summary.status),
      startedAt: formatDateTime(detail.summary.created_at),
      note: detail.logs.at(-1)?.message ?? "로그가 아직 없습니다."
    }));

    const counts = {
      default: items.filter((item) => item.status === "대기").length,
      warning: items.filter((item) => item.status === "실행 중").length,
      success: items.filter((item) => item.status === "성공").length,
      danger: items.filter((item) => item.status === "실패").length
    };

    return {
      statuses: filterPresets.jobStatuses,
      summary: [
        { label: "대기", value: String(counts.default), tone: "default" },
        { label: "실행 중", value: String(counts.warning), tone: "warning" },
        { label: "성공", value: String(counts.success), tone: "success" },
        { label: "실패", value: String(counts.danger), tone: "danger" }
      ],
      items
    };
  }
};

function toIssueCard(issue: RawIssueListResponse["items"][number]): IssueCardViewModel {
  return {
    id: issue.id,
    title: issue.title,
    category: translateIssueCategory(issue.category),
    score: issue.priority_score,
    reasons: issue.reasons
  };
}

async function fetchEvidenceReport(projectId: string): Promise<EvidencePanelItem[]> {
  const response = await request<RawEvidenceReportResponse>(`/evidence/report/${encodeURIComponent(projectId)}`);
  return response.sections.flatMap((section) =>
    section.evidences.map((evidence) => ({
      title: evidence.label,
      detail: buildEvidenceDetail(evidence),
      tone: evidence.source_kind === "market_data" || evidence.source_kind === "snapshot" ? "supplementary" : "verified"
    }))
  );
}

function formatDateTime(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) return value;
  const year = parsed.getFullYear();
  const month = String(parsed.getMonth() + 1).padStart(2, "0");
  const day = String(parsed.getDate()).padStart(2, "0");
  const hour = String(parsed.getHours()).padStart(2, "0");
  const minute = String(parsed.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day} ${hour}:${minute}`;
}

function formatPlainNumber(value: number): string {
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 2 }).format(value);
}

function formatValue(value: number, unit?: string | null): string {
  const normalized = (unit || "").toLowerCase();
  if (normalized.includes("percent") || normalized === "%") {
    return `${value.toFixed(2)}%`;
  }
  if (normalized.includes("index")) {
    return formatPlainNumber(value);
  }
  return `${formatPlainNumber(value)}${unit && !normalized.includes("index") ? ` ${unit}` : ""}`.trim();
}

function formatPercent(value: number): string {
  const prefix = value >= 0 ? "+" : "";
  return `${prefix}${value.toFixed(2)}%`;
}

function translateIssueCategory(category: string): string {
  const mapping: Record<string, string> = {
    economy: "경제",
    geopolitics: "지정학",
    investing: "투자"
  };
  return mapping[category] ?? category;
}

function translateAssetClass(assetClass: string): string {
  const mapping: Record<string, string> = {
    fx: "외환",
    equity: "주식",
    commodity: "원자재",
    rate: "금리"
  };
  return mapping[assetClass] ?? assetClass;
}

function translateJobType(jobType: string): string {
  const mapping: Record<string, string> = {
    issue_discovery: "이슈 탐색",
    snapshot_capture: "스냅샷 캡처",
    script_generation: "대본 생성",
    script_regeneration: "대본 재생성",
    image_generation: "이미지 생성",
    image_regeneration: "이미지 재생성",
    video_preparation: "영상 준비",
    video_execution: "영상 실행"
  };
  return mapping[jobType] ?? jobType;
}

function translateJobStatus(status: string): string {
  const mapping: Record<string, string> = {
    pending: "대기",
    running: "실행 중",
    success: "성공",
    failed: "실패"
  };
  return mapping[status] ?? status;
}

function buildEvidenceDetail(evidence: RawEvidenceReportResponse["sections"][number]["evidences"][number]): string {
  const suffix = evidence.value == null ? "" : `, ${formatPlainNumber(evidence.value)}`;
  const release = evidence.release_date ? `${evidence.release_date} 발표` : evidence.source.source_name;
  return `${release}${suffix}${evidence.source.note ? `, ${evidence.source.note}` : ""}`;
}

function unique<T>(values: readonly T[]): T[] {
  return Array.from(new Set(values));
}

function settingTab(category: string): string {
  return settingMetaByCategory(category)?.tab ?? category.toUpperCase();
}

function settingTitle(category: string): string {
  return settingMetaByCategory(category)?.title ?? `${category.toUpperCase()} 설정`;
}

function settingLabel(key: string): string {
  return SETTING_FIELD_META[key]?.label ?? key.replaceAll("_", " ");
}

function settingPlaceholder(key: string): string {
  return SETTING_FIELD_META[key]?.placeholder ?? "값 입력";
}

function settingMetaByCategory(category: string) {
  const mapping: Record<string, { tab: string; title: string; order: number }> = {
    api: { tab: "API", title: "모델 및 외부 API", order: 0 },
    stats: { tab: "데이터", title: "검증 및 기본 범위", order: 1 },
    storage: { tab: "저장소", title: "출력 및 저장 경로", order: 2 }
  };
  return mapping[category];
}

function settingOrder(category: string): number {
  return settingMetaByCategory(category)?.order ?? 99;
}

function mockCategoryFromTab(tab: string): string {
  const mapping: Record<string, string> = {
    API: "api",
    데이터: "stats",
    저장소: "storage"
  };
  return mapping[tab] ?? tab.toLowerCase();
}

export type {
  CharacterLibrarySnapshot,
  DashboardSnapshot,
  JobsSnapshot,
  MarketSnapshot,
  ProjectOption,
  SettingUpsertPayload,
  SettingsSnapshot,
  SnapshotCapturePayload,
  SnapshotLibraryResponse,
  SnapshotSummary,
  StatisticsSnapshot
} from "@/lib/api/types";
