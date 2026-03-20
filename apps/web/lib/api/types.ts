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
};

export type IssueCardViewModel = {
  id: string;
  title: string;
  category: string;
  score: number;
  reasons: readonly string[];
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
  items: readonly IssueCardViewModel[];
  groups: readonly { title: string; detail: string }[];
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
