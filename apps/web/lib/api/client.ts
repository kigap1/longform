import {
  createProject as createProjectMock,
  getCharacterLibrary,
  captureSnapshot as captureSnapshotMock,
  getDashboardSnapshot,
  getImageWorkspace,
  getIssueDiscoverySnapshot,
  getJobsSnapshot,
  getMarketSnapshot,
  getProjects as getProjectsMock,
  getReviewWorkspace,
  rankIssues as rankIssuesMock,
  searchWorkspace as searchWorkspaceMock,
  getScriptWorkspace,
  getSettingsSnapshot as getSettingsSnapshotMock,
  getSnapshotLibrary,
  getStatisticsSnapshot as getStatisticsSnapshotMock,
  getVideoWorkspace
} from "@/lib/api/mock-api";
import { dashboardTabs, filterPresets } from "@/lib/mock-data";
import type {
  AIProviderCatalog,
  CharacterLibrarySnapshot,
  CreateProjectPayload,
  DashboardSnapshot,
  EvidencePanelItem,
  ImageGenerationResult,
  IssueCardViewModel,
  IssueDiscoverySnapshot,
  IssueRankPayload,
  JobLogItem,
  JobsSnapshot,
  MarketSnapshot,
  ProjectOption,
  SettingUpsertPayload,
  SettingsSnapshot,
  ScriptWorkspace,
  SnapshotCapturePayload,
  SnapshotLibraryResponse,
  SnapshotSummary,
  StatisticsSnapshot,
  VideoExecutionResult,
  VideoPreparationResult,
  WorkspaceSearchResult
} from "@/lib/api/types";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";
const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, "");

function providerDisplayName(providerId: string | undefined) {
  const mapping: Record<string, string> = {
    openai: "OpenAI",
    claude: "Claude",
    gemini: "Gemini",
    kling: "Kling AI"
  };
  return mapping[(providerId ?? "").toLowerCase()] ?? (providerId || "OpenAI");
}

const SETTING_FIELD_META: Record<string, { label: string; placeholder: string }> = {
  openai_api_key: { label: "OpenAI API 키", placeholder: "비밀 키 입력" },
  openai_base_url: { label: "OpenAI Base URL", placeholder: "https://api.openai.com/v1" },
  openai_model: { label: "OpenAI 텍스트 모델", placeholder: "예: 사용할 모델" },
  openai_image_model: { label: "OpenAI 이미지 모델", placeholder: "예: 사용할 이미지 모델" },
  openai_video_model: { label: "OpenAI 비디오 모델", placeholder: "예: 사용할 비디오 모델" },
  claude_model: { label: "클로드 모델", placeholder: "모델 이름" },
  claude_api_key: { label: "Claude API 키", placeholder: "비밀 키 입력" },
  claude_api_url: { label: "Claude API URL", placeholder: "https://api.anthropic.com/v1/messages" },
  claude_api_version: { label: "Claude API 버전", placeholder: "예: 2023-06-01" },
  gemini_api_key: { label: "Gemini API 키", placeholder: "비밀 키 입력" },
  gemini_base_url: { label: "Gemini Base URL", placeholder: "https://generativelanguage.googleapis.com" },
  gemini_model: { label: "Gemini 텍스트 모델", placeholder: "예: 사용할 모델" },
  gemini_image_model: { label: "Gemini 이미지 모델", placeholder: "예: 사용할 이미지 모델" },
  gemini_video_model: { label: "Gemini 비디오 모델", placeholder: "예: 사용할 비디오 모델" },
  kling_api_key: { label: "Kling API 키", placeholder: "비밀 키 입력" },
  kling_base_url: { label: "Kling Base URL", placeholder: "https://api-app-global.klingai.com" },
  kling_video_model: { label: "Kling 비디오 모델", placeholder: "예: kling-v1" },
  kling_submit_path: { label: "Kling submit 경로", placeholder: "예: /api/video/submit 또는 브리지 URL" },
  kling_status_path: { label: "Kling status 경로", placeholder: "예: /api/video/status/{job_id}" },
  kling_result_path: { label: "Kling result 경로", placeholder: "예: /api/video/result/{job_id}" },
  script_default_provider: { label: "대본 기본 AI", placeholder: "openai / claude / gemini" },
  image_default_provider: { label: "이미지 기본 AI", placeholder: "openai / claude / gemini" },
  video_default_provider: { label: "비디오 기본 AI", placeholder: "openai / claude / gemini / kling" },
  script_provider_mode: { label: "대본 기본 모드", placeholder: "mock 또는 real" },
  image_provider_mode: { label: "이미지 기본 모드", placeholder: "mock 또는 real" },
  video_provider_mode: { label: "비디오 기본 모드", placeholder: "mock 또는 real" },
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
      country?: string;
      region?: string;
      popularity_score?: number | null;
      credibility_score?: number | null;
    }>;
    summary?: string;
    article_count?: number;
    regions?: string[];
    top_sources?: string[];
    suggested_angles?: string[];
    why_now?: string;
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

type RawAIProviderCatalogResponse = {
  items: Array<{
    id: "openai" | "claude" | "gemini" | "kling";
    label: string;
    description: string;
    order: number;
    configured: boolean;
    fields: Array<{
      key: string;
      label: string;
      placeholder: string;
      secret: boolean;
      configured: boolean;
    }>;
    stages: Array<{
      stage: "script" | "image" | "video";
      supported: boolean;
      mock_available: boolean;
      real_available: boolean;
      default_mode: string;
      note: string;
      default_selected: boolean;
    }>;
  }>;
  defaults: Record<string, string>;
};

type RawScriptSummary = {
  id: string;
  title: string;
  summary: string;
  provider_id: string;
  provider_name: string;
  provider_mode: string;
  sections: Array<{
    id: string;
    heading: string;
    content: string;
    evidence_ids: string[];
  }>;
  scenes: Array<{
    id: string;
    title: string;
    description: string;
    image_prompt: string;
    motion_prompt: string;
    evidence_ids: string[];
  }>;
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
};

type RawImageAssetSummary = {
  id: string;
  scene_id: string;
  scene_title: string;
  prompt: string;
  asset_url: string;
  thumbnail_url: string;
  status: string;
  provider_id: string;
  provider_name: string;
  provider_mode: string;
};

type RawVideoAssetSummary = {
  id: string;
  scene_id: string;
  scene_title: string;
  prompt: string;
  motion_notes: string;
  bundle_path: string;
  bundle_download_path: string;
  status: string;
  provider_id: string;
  provider_name: string;
  provider_mode: string;
  job_id: string;
};

type RawVideoExecutionSummary = {
  video_asset_id: string;
  scene_id: string;
  status: string;
  provider_id: string;
  provider_name: string;
  provider_mode: string;
  provider_job_id: string;
  output_path: string;
  bundle_path: string;
  job_id: string;
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

async function withMockFallback<T>(label: string, realFactory: () => Promise<T>, mockFactory: () => Promise<T>): Promise<T> {
  if (USE_MOCK_API) {
    return mockFactory();
  }

  try {
    return await realFactory();
  } catch (error) {
    console.warn(`[apiClient] ${label} 요청이 실패해 mock 데이터를 사용합니다.`, error);
    return mockFactory();
  }
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
  projects: async (): Promise<ProjectOption[]> =>
    withMockFallback(
      "projects",
      async () => {
        const response = await request<RawProjectListResponse>("/projects");
        return response.items.map((project) => ({
          id: project.id,
          name: project.name,
          summary: project.description || "프로젝트 설명이 아직 없습니다.",
          stage: "운영 중",
          updatedAt: formatDateTime(project.updated_at),
          issueFocus: project.issue_focus ?? undefined
        }));
      },
      () => getProjectsMock()
    ),

  createProject: async (payload: CreateProjectPayload): Promise<ProjectOption> =>
    withMockFallback(
      "createProject",
      async () => {
        const response = await request<RawProjectListResponse["items"][number]>("/projects", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        return {
          id: response.id,
          name: response.name,
          summary: response.description || "프로젝트 설명이 아직 없습니다.",
          stage: "이슈 탐색",
          updatedAt: formatDateTime(response.updated_at),
          issueFocus: response.issue_focus ?? undefined
        };
      },
      () => createProjectMock(payload)
    ),

  dashboard: async (projectId?: string): Promise<DashboardSnapshot> =>
    withMockFallback(
      "dashboard",
      async () => {
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
      () => getDashboardSnapshot(projectId)
    ),

  issues: async (projectId?: string): Promise<IssueDiscoverySnapshot> =>
    withMockFallback(
      "issues",
      async () => {
        const response = await request<RawIssueListResponse>(
          `/issues${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`
        );
        return toIssueDiscoverySnapshot(response);
      },
      () => getIssueDiscoverySnapshot(projectId)
    ),

  rankIssues: async (payload: IssueRankPayload): Promise<IssueDiscoverySnapshot> =>
    withMockFallback(
      "rankIssues",
      async () => {
        const response = await request<RawIssueListResponse>("/issues/rank", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        return toIssueDiscoverySnapshot(response);
      },
      () => rankIssuesMock(payload)
    ),

  statistics: async (projectId: string): Promise<StatisticsSnapshot> =>
    withMockFallback(
      "statistics",
      async () => {
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
      async () => {
        const snapshot = await getStatisticsSnapshotMock();
        return {
          filters: snapshot.filters,
          items: snapshot.items.map((item) => ({
            ...item,
            series: [...item.series]
          })),
          evidences: snapshot.evidences.map((item) => ({ ...item }))
        };
      }
    ),

  market: async (): Promise<MarketSnapshot> =>
    withMockFallback(
      "market",
      async () => {
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
      async () => {
        const snapshot = await getMarketSnapshot();
        return {
          periods: snapshot.periods,
          items: snapshot.items.map((item) => ({
            ...item,
            series: [...item.series]
          }))
        };
      }
    ),

  snapshots: (projectId?: string) =>
    withMockFallback(
      "snapshots",
      () => request<SnapshotLibraryResponse>(`/snapshot/list${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`),
      () => getSnapshotLibrary(projectId)
    ),

  captureSnapshot: (payload: SnapshotCapturePayload) =>
    withMockFallback(
      "captureSnapshot",
      () => request<SnapshotSummary>("/snapshot/capture", { method: "POST", body: JSON.stringify(payload) }),
      () => captureSnapshotMock(payload)
    ),

  characters: async (projectId?: string): Promise<CharacterLibrarySnapshot> =>
    withMockFallback(
      "characters",
      async () => {
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
      () => getCharacterLibrary()
    ),

  aiProviders: async (): Promise<AIProviderCatalog> =>
    withMockFallback(
      "aiProviders",
      async () => {
        const response = await request<RawAIProviderCatalogResponse>("/settings/ai-providers");
        return {
          items: response.items,
          defaults: response.defaults
        };
      },
      () => Promise.resolve(getMockAIProviderCatalog())
    ),

  scriptWorkspace: async (projectId: string): Promise<ScriptWorkspace> =>
    withMockFallback(
      "scriptWorkspace",
      async () => {
        const response = await request<RawScriptSummary | null>(`/scripts/latest?project_id=${encodeURIComponent(projectId)}`);
        if (!response) {
          return {
            scriptId: "",
            title: "생성된 대본이 아직 없습니다.",
            summary: "먼저 이슈를 선택하고 대본 생성을 실행하면 장면과 근거 매핑이 여기에 나타납니다.",
            providerId: "",
            providerName: "",
            providerMode: "mock",
            sections: [],
            scenes: [],
            evidences: []
          };
        }
        return toScriptWorkspace(response);
      },
      async () => toMockScriptWorkspace(await getScriptWorkspace())
    ),

  generateScript: async (payload: {
    project_id: string;
    issue_id: string;
    issue_summary?: string;
    user_instructions?: string;
    style_preset?: string;
    audience_type?: string;
    tone?: string;
    provider_id?: string;
    provider_mode?: string;
  }): Promise<ScriptWorkspace> =>
    withMockFallback(
      "generateScript",
      async () => {
        const response = await request<RawScriptSummary>("/scripts/generate", { method: "POST", body: JSON.stringify(payload) });
        return toScriptWorkspace(response);
      },
      async () => toMockScriptWorkspace(await getScriptWorkspace())
    ),

  regenerateScriptSection: async (payload: {
    project_id: string;
    script_id: string;
    section_id: string;
    user_instructions?: string;
    provider_id?: string;
    provider_mode?: string;
  }): Promise<{ scriptId: string; versionNumber: number; sectionId: string; content: string }> =>
    withMockFallback(
      "regenerateScriptSection",
      async () => {
        const response = await request<{
          script_id: string;
          version_number: number;
          section: { id: string; content: string };
        }>("/scripts/regenerate-section", { method: "POST", body: JSON.stringify(payload) });
        return {
          scriptId: response.script_id,
          versionNumber: response.version_number,
          sectionId: response.section.id,
          content: response.section.content
        };
      },
      async () => {
        const mock = await getScriptWorkspace();
        return {
          scriptId: "mock-script",
          versionNumber: 2,
          sectionId: mock.sections[0]?.heading ?? "mock-section",
          content: mock.sections[0]?.content ?? ""
        };
      }
    ),

  images: async (projectId: string) =>
    withMockFallback(
      "images",
      async () => {
        const workspace = await apiClient.scriptWorkspace(projectId);
        return {
          scenes: workspace.scenes.map((scene) => ({
            id: scene.id,
            title: scene.title,
            description: scene.description,
            prompt: scene.prompt,
            motion: scene.motion
          }))
        };
      },
      async () => {
        const mock = await getImageWorkspace();
        return { scenes: normalizeMockScenes(mock.scenes) };
      }
    ),

  generateImage: async (payload: {
    project_id: string;
    scene_id: string;
    prompt_override?: string;
    user_instructions?: string;
    provider_id?: string;
    provider_mode?: string;
  }): Promise<ImageGenerationResult> =>
    withMockFallback(
      "generateImage",
      async () => {
        const response = await request<RawImageAssetSummary>("/images/generate", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        return toImageResult(response);
      },
      async () => buildMockImageResult(payload)
    ),

  regenerateImage: async (payload: {
    project_id: string;
    scene_id: string;
    prompt_override?: string;
    user_instructions?: string;
    provider_id?: string;
    provider_mode?: string;
  }): Promise<ImageGenerationResult> =>
    withMockFallback(
      "regenerateImage",
      async () => {
        const response = await request<RawImageAssetSummary>("/images/regenerate-scene", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        return toImageResult(response);
      },
      async () => buildMockImageResult(payload)
    ),

  prepareVideos: async (payload: {
    project_id: string;
    scene_ids: readonly string[];
    user_instructions?: string;
    provider_id?: string;
    provider_mode?: string;
  }): Promise<VideoPreparationResult[]> =>
    withMockFallback(
      "prepareVideos",
      async () => {
        const response = await request<RawVideoAssetSummary[]>("/videos/prepare", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        return response.map(toVideoPreparationResult);
      },
      async () => buildMockVideoPreparationResults(payload)
    ),

  executeVideos: async (payload: {
    project_id: string;
    video_asset_ids: readonly string[];
    user_instructions?: string;
    provider_id?: string;
    provider_mode?: string;
  }): Promise<VideoExecutionResult[]> =>
    withMockFallback(
      "executeVideos",
      async () => {
        const response = await request<RawVideoExecutionSummary[]>("/videos/execute", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        return response.map((item) => ({
          videoAssetId: item.video_asset_id,
          sceneId: item.scene_id,
          status: item.status,
          providerId: item.provider_id,
          providerName: item.provider_name,
          providerMode: item.provider_mode,
          providerJobId: item.provider_job_id,
          outputPath: item.output_path,
          bundlePath: item.bundle_path,
          jobId: item.job_id
        }));
      },
      async () =>
        payload.video_asset_ids.map((videoAssetId, index) => ({
          videoAssetId,
          sceneId: `mock-scene-${index + 1}`,
          status: "success",
          providerId: payload.provider_id ?? "openai",
          providerName: providerDisplayName(payload.provider_id ?? "openai"),
          providerMode: payload.provider_mode ?? "mock",
          providerJobId: `mock-provider-job-${index + 1}`,
          outputPath: `/mock/${videoAssetId}.json`,
          bundlePath: `/mock/${videoAssetId}.zip`,
          jobId: `mock-job-${index + 1}`
        }))
    ),

  review: () => getReviewWorkspace(),

  settings: async (): Promise<SettingsSnapshot> =>
    withMockFallback(
      "settings",
      async () => {
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
      async () => toMockSettingsSnapshot(await getSettingsSnapshotMock())
    ),

  saveSettings: async (payloads: readonly SettingUpsertPayload[]): Promise<{ message: string }> =>
    withMockFallback(
      "saveSettings",
      async () => {
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
      () => Promise.resolve({ message: "mock settings saved" })
    ),

  jobs: async (projectId?: string): Promise<JobsSnapshot> =>
    withMockFallback(
      "jobs",
      async () => {
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
            { label: "대기", value: String(counts.default), tone: "default" as const },
            { label: "실행 중", value: String(counts.warning), tone: "warning" as const },
            { label: "성공", value: String(counts.success), tone: "success" as const },
            { label: "실패", value: String(counts.danger), tone: "danger" as const }
          ],
          items
        };
      },
      () => getJobsSnapshot(projectId)
    ),

  searchWorkspace: async (projectId: string | undefined, query: string): Promise<WorkspaceSearchResult[]> =>
    withMockFallback(
      "searchWorkspace",
      async () => {
        if (query.trim().length < 2) {
          return [];
        }

        const [projects, issues, statistics, market] = await Promise.all([
          apiClient.projects(),
          apiClient.issues(projectId),
          request<RawStatisticListResponse>("/stats/search", {
            method: "POST",
            body: JSON.stringify({ keyword: query })
          }),
          request<RawMarketSearchResponse>("/market/search", {
            method: "POST",
            body: JSON.stringify({ query })
          })
        ]);

        return [
          ...projects
            .filter((project) => matchesSearch(query, [project.name, project.summary, project.issueFocus ?? ""]))
            .slice(0, 2)
            .map((project) => ({
              id: `project-${project.id}`,
              kind: "프로젝트" as const,
              title: project.name,
              detail: project.summary,
              href: "/dashboard"
            })),
          ...issues.items
            .filter((issue) => matchesSearch(query, [issue.title, issue.summary, issue.whyNow, ...issue.youtubeAngles]))
            .slice(0, 4)
            .map((issue) => ({
              id: `issue-${issue.id}`,
              kind: "이슈" as const,
              title: issue.title,
              detail: `${issue.category} · 기사 ${issue.articleCount}건`,
              href: "/issues"
            })),
          ...statistics.items.slice(0, 3).map((item) => ({
            id: `stat-${item.indicator_code}`,
            kind: "지표" as const,
            title: item.name,
            detail: `${item.source_name} · ${formatValue(item.latest_value, item.unit)}`,
            href: "/statistics"
          })),
          ...market.items.slice(0, 3).map((item) => ({
            id: `market-${item.symbol}`,
            kind: "자산" as const,
            title: item.display_name,
            detail: `${item.symbol} · ${formatPlainNumber(item.latest_value)}`,
            href: "/market"
          }))
        ].slice(0, 8);
      },
      () => searchWorkspaceMock(projectId, query)
    )
};

function toIssueCard(issue: RawIssueListResponse["items"][number]): IssueCardViewModel {
  const articles = issue.related_articles.map((article) => ({
    id: article.id,
    title: article.title,
    sourceName: article.source_name,
    publishedAt: formatDateTime(article.published_at),
    url: article.url,
    summary: article.summary,
    country: article.country ?? inferCountryFromArticle(article.source_name, article.title),
    region: article.region ?? inferRegionFromCountry(article.country ?? inferCountryFromArticle(article.source_name, article.title)),
    popularity: Number(article.popularity_score ?? estimatePopularity(article.source_name)),
    credibility: Number(article.credibility_score ?? estimateCredibility(article.source_name))
  }));
  const regions = issue.regions?.length ? issue.regions : unique(articles.map((article) => article.country));
  const topSources = issue.top_sources?.length ? issue.top_sources : unique(articles.map((article) => article.sourceName)).slice(0, 4);

  return {
    id: issue.id,
    title: issue.title,
    category: translateIssueCategory(issue.category),
    score: issue.priority_score,
    reasons: issue.reasons,
    summary: issue.summary ?? `${issue.title} 관련 흐름을 경제 콘텐츠 관점에서 정리한 이슈입니다.`,
    articleCount: issue.article_count ?? issue.related_articles.length,
    regions,
    topSources,
    youtubeAngles: issue.suggested_angles?.length ? issue.suggested_angles : buildYoutubeAngles(issue.title),
    whyNow: issue.why_now ?? buildWhyNow(issue.title, regions),
    articles
  };
}

function toIssueDiscoverySnapshot(response: RawIssueListResponse): IssueDiscoverySnapshot {
  const items = response.items.map(toIssueCard);
  return {
    filters: filterPresets.issueCategories,
    regionFilters: ["전체", ...unique(items.flatMap((issue) => issue.regions))],
    sortOptions: ["우선순위", "최신성", "기사 수", "인기순"],
    keywordSuggestions: unique(
      items.flatMap((issue) => issue.title.split(/\s+/g).filter((token) => token.length >= 2))
    ).slice(0, 12),
    highlights: items.slice(0, 3).map((issue, index) => ({
      issueId: issue.id,
      title: issue.title,
      subtitle:
        index === 0
          ? `지금 가장 주목받는 이슈 · ${issue.articleCount}건`
          : index === 1
            ? `시장 연결성이 높은 주제 · ${issue.regions.join("/")}`
            : `콘텐츠 확장 포인트 · ${issue.youtubeAngles[0] ?? issue.summary}`,
      tone: index === 0 ? "hot" : index === 1 ? "watch" : "idea"
    })),
    lastCollectedAt: undefined,
    items,
    groups: items.map((issue) => ({
      issueId: issue.id,
      title: `${issue.title} 기사 ${issue.articleCount}건`,
      detail: issue.topSources.length ? `${issue.topSources.join(", ")} 기사 묶음` : "연결된 기사 없음",
      articleCount: issue.articleCount,
      regions: issue.regions,
      topSources: issue.topSources,
      articles: issue.articles
    }))
  };
}

function toScriptWorkspace(response: RawScriptSummary): ScriptWorkspace {
  return {
    scriptId: response.id,
    title: response.title,
    summary: response.summary,
    providerId: response.provider_id,
    providerName: response.provider_name,
    providerMode: response.provider_mode,
    sections: response.sections.map((section) => ({
      id: section.id,
      heading: section.heading,
      content: section.content,
      evidences: section.evidence_ids
    })),
    scenes: response.scenes.map((scene) => ({
      id: scene.id,
      title: scene.title,
      description: scene.description,
      prompt: scene.image_prompt,
      motion: scene.motion_prompt,
      evidenceIds: scene.evidence_ids
    })),
    evidences: response.evidences.map((evidence) => ({
      title: evidence.label,
      detail: buildEvidenceDetail({
        evidence_id: evidence.evidence_id,
        source_kind: evidence.source_kind,
        label: evidence.label,
        release_date: evidence.release_date,
        value: evidence.value,
        source: evidence.source
      }),
      tone: evidence.source_kind === "market_data" || evidence.source_kind === "snapshot" ? "supplementary" : "verified"
    }))
  };
}

function toMockScriptWorkspace(mock: Awaited<ReturnType<typeof getScriptWorkspace>>): ScriptWorkspace {
  const scenes = normalizeMockScenes(mock.scenes);
  return {
    scriptId: "mock-script",
    title: "Mock 대본 작업 공간",
    summary: "mock 데이터로 구성된 예시 대본입니다.",
    providerId: "openai",
    providerName: "OpenAI",
    providerMode: "mock",
    sections: mock.sections.map((section, index) => ({
      id: `mock-section-${index + 1}`,
      heading: section.heading,
      content: section.content,
      evidences: section.evidences
    })),
    scenes: scenes.map((scene) => ({
      id: scene.id,
      title: scene.title,
      description: scene.description,
      prompt: scene.prompt,
      motion: scene.motion,
      evidenceIds: []
    })),
    evidences: mock.evidences
  };
}

function toImageResult(response: RawImageAssetSummary): ImageGenerationResult {
  return {
    id: response.id,
    sceneId: response.scene_id,
    sceneTitle: response.scene_title,
    prompt: response.prompt,
    assetUrl: resolveApiUrl(response.asset_url),
    thumbnailUrl: resolveApiUrl(response.thumbnail_url),
    status: response.status,
    providerId: response.provider_id,
    providerName: response.provider_name,
    providerMode: response.provider_mode
  };
}

function toVideoPreparationResult(response: RawVideoAssetSummary): VideoPreparationResult {
  return {
    id: response.id,
    sceneId: response.scene_id,
    sceneTitle: response.scene_title,
    prompt: response.prompt,
    motionNotes: response.motion_notes,
    bundlePath: response.bundle_path,
    bundleDownloadPath: resolveApiUrl(response.bundle_download_path),
    status: response.status,
    providerId: response.provider_id,
    providerName: response.provider_name,
    providerMode: response.provider_mode,
    jobId: response.job_id
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

function getMockAIProviderCatalog(): AIProviderCatalog {
  return {
    defaults: {
      script: "openai",
      image: "openai",
      video: "openai"
    },
    items: [
      {
        id: "openai",
        label: "OpenAI",
        description: "대본, 이미지, 비디오 준비 mock 테스트 가능",
        order: 0,
        configured: false,
        fields: [
          { key: "openai_api_key", label: "OpenAI API 키", placeholder: "비밀 키 입력", secret: true, configured: false },
          { key: "openai_base_url", label: "OpenAI Base URL", placeholder: "https://api.openai.com/v1", secret: false, configured: false },
          { key: "openai_model", label: "OpenAI 텍스트 모델", placeholder: "예: 사용할 모델", secret: false, configured: false },
          { key: "openai_image_model", label: "OpenAI 이미지 모델", placeholder: "예: 사용할 이미지 모델", secret: false, configured: false },
          { key: "openai_video_model", label: "OpenAI 비디오 모델", placeholder: "예: 사용할 비디오 모델", secret: false, configured: false }
        ],
        stages: [
          { stage: "script", supported: true, mock_available: true, real_available: false, default_mode: "mock", note: "mock 테스트 가능", default_selected: true },
          { stage: "image", supported: true, mock_available: true, real_available: false, default_mode: "mock", note: "mock 테스트 가능", default_selected: true },
          { stage: "video", supported: true, mock_available: true, real_available: false, default_mode: "mock", note: "mock 테스트 가능", default_selected: true }
        ]
      },
      {
        id: "claude",
        label: "Claude",
        description: "대본 단계 중심 mock/real 경계",
        order: 1,
        configured: false,
        fields: [
          { key: "claude_api_key", label: "Claude API 키", placeholder: "비밀 키 입력", secret: true, configured: false },
          { key: "claude_api_url", label: "Claude API URL", placeholder: "https://api.anthropic.com/v1/messages", secret: false, configured: false },
          { key: "claude_api_version", label: "Claude API 버전", placeholder: "예: 2023-06-01", secret: false, configured: false },
          { key: "claude_model", label: "Claude 모델", placeholder: "예: 설정할 모델", secret: false, configured: false }
        ],
        stages: [
          { stage: "script", supported: true, mock_available: true, real_available: true, default_mode: "mock", note: "대본 실연동 준비됨", default_selected: false },
          { stage: "image", supported: false, mock_available: false, real_available: false, default_mode: "mock", note: "이미지 단계 미지원", default_selected: false },
          { stage: "video", supported: false, mock_available: false, real_available: false, default_mode: "mock", note: "비디오 단계 미지원", default_selected: false }
        ]
      },
      {
        id: "gemini",
        label: "Gemini",
        description: "대본, 이미지, 비디오 준비 mock 테스트 가능",
        order: 2,
        configured: false,
        fields: [
          { key: "gemini_api_key", label: "Gemini API 키", placeholder: "비밀 키 입력", secret: true, configured: false },
          { key: "gemini_base_url", label: "Gemini Base URL", placeholder: "https://generativelanguage.googleapis.com", secret: false, configured: false },
          { key: "gemini_model", label: "Gemini 텍스트 모델", placeholder: "예: 사용할 모델", secret: false, configured: false },
          { key: "gemini_image_model", label: "Gemini 이미지 모델", placeholder: "예: 사용할 이미지 모델", secret: false, configured: false },
          { key: "gemini_video_model", label: "Gemini 비디오 모델", placeholder: "예: 사용할 비디오 모델", secret: false, configured: false }
        ],
        stages: [
          { stage: "script", supported: true, mock_available: true, real_available: false, default_mode: "mock", note: "mock 테스트 가능", default_selected: false },
          { stage: "image", supported: true, mock_available: true, real_available: false, default_mode: "mock", note: "mock 테스트 가능", default_selected: false },
          { stage: "video", supported: true, mock_available: true, real_available: false, default_mode: "mock", note: "mock 테스트 가능", default_selected: false }
        ]
      },
      {
        id: "kling",
        label: "Kling AI",
        description: "비디오 단계용 mock 테스트와 브리지형 real 경계",
        order: 3,
        configured: false,
        fields: [
          { key: "kling_api_key", label: "Kling API 키", placeholder: "비밀 키 입력", secret: true, configured: false },
          { key: "kling_base_url", label: "Kling Base URL", placeholder: "https://api-app-global.klingai.com", secret: false, configured: false },
          { key: "kling_video_model", label: "Kling 비디오 모델", placeholder: "예: kling-v1", secret: false, configured: false },
          { key: "kling_submit_path", label: "Kling submit 경로", placeholder: "예: /api/video/submit 또는 브리지 URL", secret: false, configured: false },
          { key: "kling_status_path", label: "Kling status 경로", placeholder: "예: /api/video/status/{job_id}", secret: false, configured: false },
          { key: "kling_result_path", label: "Kling result 경로", placeholder: "예: /api/video/result/{job_id}", secret: false, configured: false }
        ],
        stages: [
          { stage: "script", supported: false, mock_available: false, real_available: false, default_mode: "mock", note: "대본 단계 미지원", default_selected: false },
          { stage: "image", supported: false, mock_available: false, real_available: false, default_mode: "mock", note: "이미지 단계 미지원", default_selected: false },
          {
            stage: "video",
            supported: true,
            mock_available: true,
            real_available: true,
            default_mode: "mock",
            note: "mock 테스트 가능, real 모드는 submit/status/result 경로 설정이 필요",
            default_selected: false
          }
        ]
      }
    ]
  };
}

async function buildMockImageResult(payload: {
  scene_id: string;
  prompt_override?: string;
  provider_id?: string;
  provider_mode?: string;
}): Promise<ImageGenerationResult> {
  const scenes = normalizeMockScenes((await getImageWorkspace()).scenes);
  const match = scenes.find((item) => item.id === payload.scene_id) ?? scenes[0];
  return {
    id: `mock-image-${payload.scene_id}`,
    sceneId: payload.scene_id,
    sceneTitle: match?.title ?? "장면",
    prompt: payload.prompt_override || match?.prompt || "",
    assetUrl: `https://placehold.co/1024x1536/png?text=${encodeURIComponent(payload.scene_id)}`,
    thumbnailUrl: `https://placehold.co/256x384/png?text=${encodeURIComponent(payload.scene_id)}`,
    status: "ready",
    providerId: payload.provider_id ?? "openai",
    providerName: providerDisplayName(payload.provider_id ?? "openai"),
    providerMode: payload.provider_mode ?? "mock"
  };
}

async function buildMockVideoPreparationResults(payload: {
  scene_ids: readonly string[];
  provider_id?: string;
  provider_mode?: string;
}): Promise<VideoPreparationResult[]> {
  const scenes = normalizeMockScenes((await getVideoWorkspace()).scenes);
  return scenes
    .filter((scene) => payload.scene_ids.includes(scene.id))
    .map((scene, index) => ({
      id: `mock-video-${scene.id}-${index + 1}`,
      sceneId: scene.id,
      sceneTitle: scene.title,
      prompt: scene.prompt,
      motionNotes: scene.motion,
      bundlePath: `/mock/${scene.id}.zip`,
      bundleDownloadPath: `/mock/${scene.id}.zip`,
      status: "ready",
      providerId: payload.provider_id ?? "openai",
      providerName: providerDisplayName(payload.provider_id ?? "openai"),
      providerMode: payload.provider_mode ?? "mock",
      jobId: `mock-job-${index + 1}`
    }));
}

function toMockSettingsSnapshot(snapshot: Awaited<ReturnType<typeof getSettingsSnapshotMock>>): SettingsSnapshot {
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

function buildYoutubeAngles(title: string) {
  return [
    `${title}를 3가지 숫자로 설명`,
    `${title}가 한국 시장에 주는 영향`,
    `${title}를 볼 때 같이 확인할 지표`
  ];
}

function buildWhyNow(title: string, regions: readonly string[]) {
  const regionText = regions.length ? `${regions.join(", ")} 기사 흐름이 동시에 붙었습니다.` : "복수 매체 보도가 이어지고 있습니다.";
  return `${title}는 최근 보도량과 시장 파급력이 함께 커진 주제입니다. ${regionText}`;
}

function inferCountryFromArticle(sourceName: string, title: string) {
  const source = `${sourceName} ${title}`.toLowerCase();
  if (/[가-힣]/.test(sourceName)) {
    return "한국";
  }
  if (source.includes("reuters") || source.includes("bloomberg") || source.includes("wsj") || source.includes("seeking alpha")) {
    return "미국";
  }
  if (source.includes("nikkei") || source.includes("니혼게이자이") || source.includes("japan") || source.includes("boj")) {
    return "일본";
  }
  if (source.includes("caixin") || source.includes("china daily") || source.includes("신화")) {
    return "중국";
  }
  return "글로벌";
}

function inferRegionFromCountry(country: string) {
  if (country === "한국" || country === "중국" || country === "일본") return "아시아";
  if (country === "미국") return "북미";
  return "글로벌";
}

function estimatePopularity(sourceName: string) {
  const source = sourceName.toLowerCase();
  if (source.includes("reuters") || source.includes("bloomberg")) return 90;
  if (source.includes("wsj") || source.includes("연합뉴스")) return 86;
  return 76;
}

function estimateCredibility(sourceName: string) {
  const source = sourceName.toLowerCase();
  if (source.includes("reuters") || source.includes("bloomberg")) return 0.92;
  if (source.includes("wsj") || source.includes("연합뉴스")) return 0.88;
  return 0.8;
}

function matchesSearch(query: string, fields: readonly string[]) {
  const normalized = query.trim().toLowerCase();
  return fields.some((field) => field.toLowerCase().includes(normalized));
}

function unique<T>(values: readonly T[]): T[] {
  return Array.from(new Set(values));
}

function normalizeMockScenes(
  scenes: ReadonlyArray<{ title: string; description: string; prompt: string; motion: string }>
) {
  return scenes.map((scene, index) => ({
    id: `mock-scene-${index + 1}`,
    ...scene
  }));
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
  AIProviderCatalog,
  CharacterLibrarySnapshot,
  DashboardSnapshot,
  ImageGenerationResult,
  IssueRankPayload,
  JobsSnapshot,
  MarketSnapshot,
  ProjectOption,
  SettingUpsertPayload,
  SettingsSnapshot,
  ScriptWorkspace,
  SnapshotCapturePayload,
  SnapshotLibraryResponse,
  SnapshotSummary,
  StatisticsSnapshot,
  VideoExecutionResult,
  VideoPreparationResult
} from "@/lib/api/types";
