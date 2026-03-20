"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient, type SettingUpsertPayload, type SnapshotCapturePayload } from "@/lib/api/client";
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

export function useStatisticsQuery(projectId: string) {
  return useQuery({
    queryKey: ["statistics", projectId],
    queryFn: () => apiClient.statistics(projectId),
    enabled: Boolean(projectId)
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

export function useVideosQuery() {
  return useQuery({
    queryKey: ["mock", "videos"],
    queryFn: getVideoWorkspace
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
