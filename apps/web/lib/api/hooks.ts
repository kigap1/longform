"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  apiClient,
  type IssueRankPayload,
  type SettingUpsertPayload,
  type SnapshotCapturePayload
} from "@/lib/api/client";
import {
  getImageWorkspace,
  getReviewWorkspace,
  getScriptWorkspace,
  getVideoWorkspace
} from "@/lib/api/mock-api";


export function useProjectsQuery() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: () => apiClient.projects()
  });
}

export function useCreateProjectMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.createProject>[0]) => apiClient.createProject(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["projects"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      await queryClient.invalidateQueries({ queryKey: ["issues"] });
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  });
}

export function useDashboardQuery(projectId?: string) {
  return useQuery({
    queryKey: ["dashboard", projectId ?? "current"],
    queryFn: () => apiClient.dashboard(projectId)
  });
}

export function useIssuesQuery(projectId?: string) {
  return useQuery({
    queryKey: ["issues", projectId ?? "current"],
    queryFn: () => apiClient.issues(projectId)
  });
}

export function useRankIssuesMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: IssueRankPayload) => apiClient.rankIssues(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["issues"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["issues", projectId] });
        await queryClient.invalidateQueries({ queryKey: ["dashboard", projectId] });
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useStatisticsQuery(projectId?: string) {
  return useQuery({
    queryKey: ["statistics", projectId ?? "default"],
    queryFn: () => apiClient.statistics(projectId ?? "project-1")
  });
}

export function useMarketQuery() {
  return useQuery({
    queryKey: ["market"],
    queryFn: () => apiClient.market()
  });
}

export function useSnapshotsQuery(projectId?: string) {
  return useQuery({
    queryKey: ["snapshots", projectId ?? "all"],
    queryFn: () => apiClient.snapshots(projectId)
  });
}

export function useCaptureSnapshotMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SnapshotCapturePayload) => apiClient.captureSnapshot(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["snapshots"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["snapshots", projectId] });
      }
    }
  });
}

export function useScriptsQuery() {
  return useQuery({
    queryKey: ["mock", "scripts"],
    queryFn: getScriptWorkspace
  });
}

export function useAIProvidersQuery() {
  return useQuery({
    queryKey: ["ai-providers"],
    queryFn: () => apiClient.aiProviders()
  });
}

export function useScriptWorkspaceQuery(projectId?: string) {
  return useQuery({
    queryKey: ["script-workspace", projectId ?? "default"],
    queryFn: () => apiClient.scriptWorkspace(projectId ?? "project-1")
  });
}

export function useGenerateScriptMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.generateScript>[0]) => apiClient.generateScript(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["script-workspace"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["script-workspace", projectId] });
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useRegenerateScriptSectionMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.regenerateScriptSection>[0]) => apiClient.regenerateScriptSection(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["script-workspace"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["script-workspace", projectId] });
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useCharactersQuery(projectId?: string) {
  return useQuery({
    queryKey: ["characters", projectId ?? "current"],
    queryFn: () => apiClient.characters(projectId)
  });
}

export function useImagesQuery() {
  return useQuery({
    queryKey: ["mock", "images"],
    queryFn: getImageWorkspace
  });
}

export function useImageWorkspaceQuery(projectId?: string) {
  return useQuery({
    queryKey: ["image-workspace", projectId ?? "default"],
    queryFn: () => apiClient.images(projectId ?? "project-1")
  });
}

export function useGenerateImageMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.generateImage>[0]) => apiClient.generateImage(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["image-workspace"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["image-workspace", projectId] });
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useRegenerateImageMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.regenerateImage>[0]) => apiClient.regenerateImage(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["image-workspace"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["image-workspace", projectId] });
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useVideosQuery() {
  return useQuery({
    queryKey: ["mock", "videos"],
    queryFn: getVideoWorkspace
  });
}

export function useVideoWorkspaceQuery(projectId?: string) {
  return useQuery({
    queryKey: ["video-workspace", projectId ?? "default"],
    queryFn: () => apiClient.images(projectId ?? "project-1")
  });
}

export function usePrepareVideosMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.prepareVideos>[0]) => apiClient.prepareVideos(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useExecuteVideosMutation(projectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof apiClient.executeVideos>[0]) => apiClient.executeVideos(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
      if (projectId) {
        await queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      }
    }
  });
}

export function useReviewQuery() {
  return useQuery({
    queryKey: ["mock", "review"],
    queryFn: getReviewWorkspace
  });
}

export function useSettingsQuery() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: () => apiClient.settings()
  });
}

export function useSaveSettingsMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payloads: readonly SettingUpsertPayload[]) => apiClient.saveSettings(payloads),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["settings"] });
    }
  });
}

export function useJobsQuery(projectId?: string) {
  return useQuery({
    queryKey: ["jobs", projectId ?? "current"],
    queryFn: () => apiClient.jobs(projectId)
  });
}

export function useWorkspaceSearchQuery(projectId: string | undefined, query: string) {
  return useQuery({
    queryKey: ["workspace-search", projectId ?? "current", query],
    queryFn: () => apiClient.searchWorkspace(projectId, query),
    enabled: query.trim().length >= 2
  });
}
