import {
  dashboardTabs,
  evidenceItems,
  filterPresets,
  marketRows,
  scenes,
  scriptSections,
  settingsSections,
  snapshots as snapshotSeed,
  statisticsRows
} from "@/lib/mock-data";
import type {
  CreateProjectPayload,
  SnapshotCapturePayload,
  SnapshotLibraryResponse,
  SnapshotSummary,
  WorkspaceSearchResult
} from "@/lib/api/types";
import {
  createMockProject,
  getMockDashboardSnapshot,
  getMockIssueDiscoverySnapshot,
  getMockJobsSnapshot,
  listMockProjects,
  rankMockIssues,
  searchMockWorkspace
} from "@/lib/mock-studio-engine";


export type ProjectOption = Awaited<ReturnType<typeof listMockProjects>>[number];
export type DashboardTab = (typeof dashboardTabs)[number];
export type StatisticRow = (typeof statisticsRows)[number];
export type MarketRow = (typeof marketRows)[number];
export type SnapshotItem = SnapshotSummary;
export type ScriptSection = (typeof scriptSections)[number];
export type SceneItem = (typeof scenes)[number];
export type EvidenceItem = (typeof evidenceItems)[number];
export type SettingsSection = (typeof settingsSections)[number];

const delay = async (ms = 120) => new Promise((resolve) => setTimeout(resolve, ms));
const jobSummary = [
  { label: "대기", value: "3", tone: "default" },
  { label: "실행 중", value: "2", tone: "warning" },
  { label: "성공", value: "18", tone: "success" },
  { label: "실패", value: "1", tone: "danger" }
] as const;
let snapshotStore: SnapshotSummary[] = snapshotSeed.map(cloneSnapshot);

export async function getProjects() {
  await delay();
  return listMockProjects();
}

export async function createProject(payload: CreateProjectPayload) {
  await delay();
  return createMockProject(payload);
}

export async function getDashboardSnapshot(projectId?: string) {
  await delay();
  return getMockDashboardSnapshot(projectId);
}

export async function getIssueDiscoverySnapshot(projectId?: string) {
  await delay();
  return getMockIssueDiscoverySnapshot(projectId);
}

export async function rankIssues(payload: {
  project_id?: string;
  keywords?: readonly string[];
  user_instructions?: string;
}) {
  await delay();
  return rankMockIssues(payload);
}

export async function getStatisticsSnapshot() {
  await delay();
  return {
    filters: filterPresets.dataFreshness,
    items: [...statisticsRows],
    evidences: [...evidenceItems]
  };
}

export async function getMarketSnapshot() {
  await delay();
  return {
    periods: filterPresets.periods,
    items: [...marketRows]
  };
}

export async function getSnapshotLibrary(projectId?: string): Promise<SnapshotLibraryResponse> {
  await delay();
  return {
    periods: filterPresets.periods,
    items: snapshotStore
      .filter((item) => !projectId || item.project_id === projectId)
      .map(cloneSnapshot)
  };
}

export async function captureSnapshot(payload: SnapshotCapturePayload): Promise<SnapshotSummary> {
  await delay();
  const sourceTitle = deriveSourceTitle(payload.source_url, payload.source_title);
  const title = `${sourceTitle} 캡처`;
  const created: SnapshotSummary = {
    id: `snapshot-${snapshotStore.length + 1}`,
    project_id: payload.project_id,
    title,
    source_title: sourceTitle,
    image_url: `https://placehold.co/1200x675/png?text=${encodeURIComponent(title)}`,
    preview_url: `https://placehold.co/1200x675/png?text=${encodeURIComponent(title)}`,
    source_url: payload.source_url,
    captured_at: new Date().toISOString().slice(0, 16).replace("T", " "),
    capture_mode: "stub",
    integration_boundary_note: "실제 브라우저 캡처는 아직 연결되지 않았습니다. 현재는 stub 썸네일과 메타데이터만 저장합니다.",
    note: payload.note,
    attached_evidences:
      payload.attach_as_evidence === false
        ? []
        : [
            {
              evidence_id: `snapshot-evidence-${snapshotStore.length + 1}`,
              source_kind: "snapshot",
              label: payload.evidence_label || title,
              source: {
                source_name: "Mock Snapshot",
                source_url: payload.source_url,
                note: payload.note
              }
            }
          ]
  };
  snapshotStore = [created, ...snapshotStore];
  return cloneSnapshot(created);
}

export async function getScriptWorkspace() {
  await delay();
  return {
    sections: [...scriptSections],
    evidences: [...evidenceItems],
    scenes: [...scenes]
  };
}

export async function getCharacterLibrary() {
  await delay();
  return {
    items: [
      {
        id: "character-1",
        name: "한결 앵커",
        description: "차분하고 신뢰감 있는 경제 전문 진행자",
        rules: ["네이비 수트", "따뜻한 표정", "정면 구도 우선"],
        locked: true
      },
      {
        id: "character-2",
        name: "지안 애널리스트",
        description: "데이터 설명에 강한 분석형 캐릭터",
        rules: ["베이지 재킷", "차트 포인팅", "보드형 인포그래픽"],
        locked: false
      }
    ]
  };
}

export async function getImageWorkspace() {
  await delay();
  return {
    scenes: [...scenes]
  };
}

export async function getVideoWorkspace() {
  await delay();
  return {
    scenes: [...scenes]
  };
}

export async function getReviewWorkspace() {
  await delay();
  return {
    sections: [...scriptSections],
    evidences: [...evidenceItems]
  };
}

export async function getSettingsSnapshot() {
  await delay();
  return {
    tabs: settingsSections.map((section) => section.tab),
    sections: [...settingsSections]
  };
}

export async function getJobsSnapshot(projectId?: string) {
  await delay();
  return getMockJobsSnapshot(projectId);
}

export async function searchWorkspace(projectId: string | undefined, query: string): Promise<WorkspaceSearchResult[]> {
  await delay(80);
  return searchMockWorkspace(projectId, query);
}

function cloneSnapshot(snapshot: SnapshotSummary): SnapshotSummary {
  return {
    ...snapshot,
    attached_evidences: snapshot.attached_evidences.map((evidence) => ({
      ...evidence,
      source: { ...evidence.source }
    }))
  };
}

function deriveSourceTitle(url: string, fallback?: string) {
  if (fallback?.trim()) return fallback.trim();
  try {
    return new URL(url).host || "Snapshot Source";
  } catch {
    return "Snapshot Source";
  }
}
