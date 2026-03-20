"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";


type ProjectScopedState = {
  stageInstructions: Record<string, string>;
  stageProviders: Record<string, string>;
  selectedIssueId: string;
};

function createDefaultProjectScopedState(): ProjectScopedState {
  return {
    stageInstructions: {},
    stageProviders: {
      scripts: "openai",
      images: "openai",
      videos: "openai"
    },
    selectedIssueId: ""
  };
}

function resolveProjectState(
  projectStateById: Record<string, ProjectScopedState>,
  projectId: string
): ProjectScopedState {
  return projectStateById[projectId] ?? createDefaultProjectScopedState();
}


type ProjectState = {
  currentProjectId: string;
  currentProjectName: string;
  stageInstructions: Record<string, string>;
  stageProviders: Record<string, string>;
  selectedIssueId: string;
  projectStateById: Record<string, ProjectScopedState>;
  setProject: (id: string, name: string) => void;
  setStageInstruction: (stage: string, value: string) => void;
  setStageProvider: (stage: string, providerId: string) => void;
  selectIssue: (issueId: string) => void;
};

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      currentProjectId: "project-1",
      currentProjectName: "미국 금리와 원화 변동성",
      stageInstructions: {},
      stageProviders: createDefaultProjectScopedState().stageProviders,
      selectedIssueId: "",
      projectStateById: {
        "project-1": createDefaultProjectScopedState()
      },
      setProject: (id, name) =>
        set((state) => {
          const nextProjectState = resolveProjectState(state.projectStateById, id);
          return {
            currentProjectId: id,
            currentProjectName: name,
            stageInstructions: nextProjectState.stageInstructions,
            stageProviders: nextProjectState.stageProviders,
            selectedIssueId: nextProjectState.selectedIssueId,
            projectStateById: {
              ...state.projectStateById,
              [id]: nextProjectState
            }
          };
        }),
      setStageInstruction: (stage, value) =>
        set((state) => ({
          stageInstructions: {
            ...state.stageInstructions,
            [stage]: value
          },
          projectStateById: {
            ...state.projectStateById,
            [state.currentProjectId]: {
              ...resolveProjectState(state.projectStateById, state.currentProjectId),
              stageInstructions: {
                ...state.stageInstructions,
                [stage]: value
              }
            }
          }
        })),
      setStageProvider: (stage, providerId) =>
        set((state) => ({
          stageProviders: {
            ...state.stageProviders,
            [stage]: providerId
          },
          projectStateById: {
            ...state.projectStateById,
            [state.currentProjectId]: {
              ...resolveProjectState(state.projectStateById, state.currentProjectId),
              stageProviders: {
                ...state.stageProviders,
                [stage]: providerId
              }
            }
          }
        })),
      selectIssue: (issueId) =>
        set((state) => ({
          selectedIssueId: issueId,
          projectStateById: {
            ...state.projectStateById,
            [state.currentProjectId]: {
              ...resolveProjectState(state.projectStateById, state.currentProjectId),
              selectedIssueId: issueId
            }
          }
        }))
    }),
    {
      name: "factstudio.project-store"
    }
  )
);
