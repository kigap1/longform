"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useCreateProjectMutation, useProjectsQuery } from "@/lib/api/hooks";
import { OPEN_PROJECT_CREATOR_EVENT } from "@/lib/project-events";
import { useProjectStore } from "@/lib/stores/project-store";


export function ProjectSelector() {
  const { data: projects = [] } = useProjectsQuery();
  const createProject = useCreateProjectMutation();
  const currentProjectId = useProjectStore((state) => state.currentProjectId);
  const setProject = useProjectStore((state) => state.setProject);
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    issue_focus: ""
  });

  useEffect(() => {
    if (!projects.length) return;
    const current = projects.find((project) => project.id === currentProjectId) ?? projects[0];
    setProject(current.id, current.name);
  }, [projects, currentProjectId, setProject]);

  useEffect(() => {
    function handleOpenComposer() {
      setIsComposerOpen(true);
    }

    window.addEventListener(OPEN_PROJECT_CREATOR_EVENT, handleOpenComposer);
    return () => window.removeEventListener(OPEN_PROJECT_CREATOR_EVENT, handleOpenComposer);
  }, []);

  async function handleCreateProject() {
    if (!form.name.trim()) return;
    const created = await createProject.mutateAsync({
      name: form.name.trim(),
      description: form.description.trim(),
      issue_focus: form.issue_focus.trim()
    });
    setProject(created.id, created.name);
    setForm({ name: "", description: "", issue_focus: "" });
    setIsComposerOpen(false);
  }

  return (
    <div className="min-w-[280px]">
      <div className="flex items-end gap-2">
        <div className="flex-1">
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
        <Button type="button" variant="secondary" onClick={() => setIsComposerOpen((value) => !value)}>
          새 프로젝트
        </Button>
      </div>

      {isComposerOpen ? (
        <div className="mt-3 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="space-y-3">
            <Input
              value={form.name}
              placeholder="프로젝트 이름"
              onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            />
            <Textarea
              className="min-h-20"
              value={form.description}
              placeholder="프로젝트 설명"
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
            />
            <Input
              value={form.issue_focus}
              placeholder="예: 금리, 환율, 한국 증시"
              onChange={(event) => setForm((current) => ({ ...current, issue_focus: event.target.value }))}
            />
          </div>

          {createProject.isError ? (
            <div className="mt-3 rounded-2xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
              {createProject.error instanceof Error ? createProject.error.message : "프로젝트 생성 중 오류가 발생했습니다."}
            </div>
          ) : null}

          <div className="mt-4 flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setIsComposerOpen(false)}>
              닫기
            </Button>
            <Button type="button" onClick={() => void handleCreateProject()} disabled={createProject.isPending || !form.name.trim()}>
              {createProject.isPending ? "생성 중..." : "생성"}
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
