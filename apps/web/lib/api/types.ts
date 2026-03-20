export type SnapshotEvidenceReference = {
  evidence_id: string;
  source_kind: string;
  label: string;
  indicator_code?: string | null;
  release_date?: string | null;
  value?: number | null;
  source: {
    source_name: string;
    source_url: string;
    captured_at?: string | null;
    note?: string | null;
  };
};

export type SnapshotSummary = {
  id: string;
  project_id: string;
  title: string;
  source_title: string;
  image_url: string;
  preview_url: string;
  source_url: string;
  captured_at: string;
  capture_mode: string;
  integration_boundary_note?: string | null;
  note?: string | null;
  attached_evidences: readonly SnapshotEvidenceReference[];
};

export type SnapshotLibraryResponse = {
  periods: readonly string[];
  items: readonly SnapshotSummary[];
};

export type SnapshotCapturePayload = {
  project_id: string;
  source_url: string;
  source_title?: string;
  note?: string;
  attach_as_evidence?: boolean;
  evidence_label?: string;
};

export type ProjectOption = {
  id: string;
  name: string;
  summary: string;
  stage: string;
  updatedAt: string;
  issueFocus?: string;
};

export type CreateProjectPayload = {
  name: string;
  description?: string;
  issue_focus?: string;
};

export type IssueRankPayload = {
  project_id?: string;
  category?: string;
  keywords?: readonly string[];
  user_instructions?: string;
};

export type IssueArticleViewModel = {
  id: string;
  title: string;
  sourceName: string;
  publishedAt: string;
  url: string;
  summary: string;
  country: string;
  region: string;
  popularity: number;
  credibility: number;
};

export type IssueCardViewModel = {
  id: string;
  title: string;
  category: string;
  score: number;
  reasons: readonly string[];
  summary: string;
  articleCount: number;
  regions: readonly string[];
  topSources: readonly string[];
  youtubeAngles: readonly string[];
  whyNow: string;
  articles: readonly IssueArticleViewModel[];
};

export type IssueGroupViewModel = {
  issueId: string;
  title: string;
  detail: string;
  articleCount: number;
  regions: readonly string[];
  topSources: readonly string[];
  articles: readonly IssueArticleViewModel[];
};

export type IssueHighlightViewModel = {
  issueId: string;
  title: string;
  subtitle: string;
  tone: "hot" | "watch" | "idea";
};

export type EvidencePanelItem = {
  title: string;
  detail: string;
  tone: "verified" | "supplementary";
};

export type JobLogItem = {
  id?: string;
  type: string;
  status: string;
  startedAt: string;
  note: string;
};

export type DashboardMetric = {
  label: string;
  value: string;
  change: string;
};

export type DashboardSnapshot = {
  metrics: readonly DashboardMetric[];
  tabs: readonly string[];
  issues: readonly IssueCardViewModel[];
  evidences: readonly EvidencePanelItem[];
  jobs: readonly JobLogItem[];
};

export type IssueDiscoverySnapshot = {
  filters: readonly string[];
  regionFilters: readonly string[];
  sortOptions: readonly string[];
  keywordSuggestions: readonly string[];
  highlights: readonly IssueHighlightViewModel[];
  lastCollectedAt?: string;
  items: readonly IssueCardViewModel[];
  groups: readonly IssueGroupViewModel[];
};

export type StatisticRowViewModel = {
  code: string;
  name: string;
  source: string;
  latest: string;
  previous: string;
  releaseDate: string;
  stale: boolean;
  series: readonly number[];
};

export type StatisticsSnapshot = {
  filters: readonly string[];
  items: readonly StatisticRowViewModel[];
  evidences: readonly EvidencePanelItem[];
};

export type MarketRowViewModel = {
  symbol: string;
  name: string;
  className: string;
  value: string;
  change: string;
  source: string;
  series: readonly number[];
};

export type MarketSnapshot = {
  periods: readonly string[];
  items: readonly MarketRowViewModel[];
};

export type CharacterLibrarySnapshot = {
  items: readonly {
    id: string;
    name: string;
    description: string;
    rules: readonly string[];
    locked: boolean;
  }[];
};

export type AIProviderField = {
  key: string;
  label: string;
  placeholder: string;
  secret?: boolean;
  configured?: boolean;
};

export type AIProviderStageSupport = {
  stage: "script" | "image" | "video";
  supported: boolean;
  mock_available: boolean;
  real_available: boolean;
  default_mode: string;
  note: string;
  default_selected: boolean;
};

export type AIProviderItem = {
  id: "openai" | "claude" | "gemini" | "kling";
  label: string;
  description: string;
  order: number;
  configured: boolean;
  fields: readonly AIProviderField[];
  stages: readonly AIProviderStageSupport[];
};

export type AIProviderCatalog = {
  items: readonly AIProviderItem[];
  defaults: Record<string, string>;
};

export type SettingsField = {
  category: string;
  key: string;
  label: string;
  value: string;
  placeholder: string;
  secret?: boolean;
};

export type SettingsSection = {
  category: string;
  tab: string;
  title: string;
  fields: readonly SettingsField[];
};

export type SettingsSnapshot = {
  tabs: readonly string[];
  sections: readonly SettingsSection[];
};

export type SettingUpsertPayload = {
  category: string;
  key: string;
  value: string;
  secret?: boolean;
};

export type JobsSnapshot = {
  statuses: readonly string[];
  summary: readonly { label: string; value: string; tone: "default" | "success" | "warning" | "danger" }[];
  items: readonly JobLogItem[];
};

export type ScriptWorkspace = {
  scriptId: string;
  title: string;
  summary: string;
  providerId: string;
  providerName: string;
  providerMode: string;
  sections: readonly {
    id: string;
    heading: string;
    content: string;
    evidences: readonly string[];
  }[];
  scenes: readonly {
    id: string;
    title: string;
    description: string;
    prompt: string;
    motion: string;
    evidenceIds: readonly string[];
  }[];
  evidences: readonly EvidencePanelItem[];
};

export type ImageGenerationResult = {
  id: string;
  sceneId: string;
  sceneTitle: string;
  prompt: string;
  assetUrl: string;
  thumbnailUrl: string;
  status: string;
  providerId: string;
  providerName: string;
  providerMode: string;
};

export type VideoPreparationResult = {
  id: string;
  sceneId: string;
  sceneTitle: string;
  prompt: string;
  motionNotes: string;
  bundlePath: string;
  bundleDownloadPath: string;
  status: string;
  providerId: string;
  providerName: string;
  providerMode: string;
  jobId: string;
};

export type VideoExecutionResult = {
  videoAssetId: string;
  sceneId: string;
  status: string;
  providerId: string;
  providerName: string;
  providerMode: string;
  providerJobId: string;
  outputPath: string;
  bundlePath: string;
  jobId: string;
};

export type WorkspaceSearchResult = {
  id: string;
  kind: "프로젝트" | "이슈" | "지표" | "자산";
  title: string;
  detail: string;
  href: string;
};
