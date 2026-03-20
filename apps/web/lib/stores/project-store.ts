"use client";

import { create } from "zustand";


type ProjectState = {
  currentProjectId: string;
  currentProjectName: string;
  stageInstructions: Record<string, string>;
  setProject: (id: string, name: string) => void;
  setStageInstruction: (stage: string, value: string) => void;
};

export const useProjectStore = create<ProjectState>((set) => ({
  currentProjectId: "project-1",
  currentProjectName: "미국 금리와 원화 변동성",
  stageInstructions: {},
  setProject: (id, name) => set({ currentProjectId: id, currentProjectName: name }),
  setStageInstruction: (stage, value) =>
    set((state) => ({
      stageInstructions: {
        ...state.stageInstructions,
        [stage]: value
      }
    }))
}));

