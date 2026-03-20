"use client";

import { create } from "zustand";


type ProjectState = {
  currentProjectId: string;
  currentProjectName: string;
  stageInstructions: Record<string, string>;
  stageProviders: Record<string, string>;
  setProject: (id: string, name: string) => void;
  setStageInstruction: (stage: string, value: string) => void;
  setStageProvider: (stage: string, providerId: string) => void;
};

export const useProjectStore = create<ProjectState>((set) => ({
  currentProjectId: "project-1",
  currentProjectName: "미국 금리와 원화 변동성",
  stageInstructions: {},
  stageProviders: {
    scripts: "openai",
    images: "openai",
    videos: "openai"
  },
  setProject: (id, name) => set({ currentProjectId: id, currentProjectName: name }),
  setStageInstruction: (stage, value) =>
    set((state) => ({
      stageInstructions: {
        ...state.stageInstructions,
        [stage]: value
      }
    })),
  setStageProvider: (stage, providerId) =>
    set((state) => ({
      stageProviders: {
        ...state.stageProviders,
        [stage]: providerId
      }
    }))
}));
