"use client";

import { useEffect } from "react";

import { Select } from "@/components/ui/select";
import { useProjectsQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export function ProjectSelector() {
  const { data: projects = [] } = useProjectsQuery();
  const currentProjectId = useProjectStore((state) => state.currentProjectId);
  const setProject = useProjectStore((state) => state.setProject);

  useEffect(() => {
    if (!projects.length) return;
    const current = projects.find((project) => project.id === currentProjectId) ?? projects[0];
    setProject(current.id, current.name);
  }, [projects, currentProjectId, setProject]);

  return (
    <div className="min-w-[240px]">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">프로젝트 선택</p>
      <Select
        value={currentProjectId}
        onChange={(event) => {
          const next = projects.find((project) => project.id === event.target.value);
          if (next) setProject(next.id, next.name);
        }}
      >
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </Select>
    </div>
  );
}

