"use client";

import { useEffect, useState } from "react";

import { AIProviderSelector } from "@/components/shared/ai-provider-selector";
import { EvidencePanel } from "@/components/shared/evidence-panel";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  useAIProvidersQuery,
  useGenerateScriptMutation,
  useIssuesQuery,
  useRegenerateScriptSectionMutation,
  useScriptWorkspaceQuery
} from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function ScriptsPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const stageInstruction = useProjectStore((state) => state.stageInstructions.scripts ?? "");
  const stageProvider = useProjectStore((state) => state.stageProviders.scripts ?? "");
  const storedSelectedIssueId = useProjectStore((state) => state.selectedIssueId);
  const setStageProvider = useProjectStore((state) => state.setStageProvider);
  const selectIssue = useProjectStore((state) => state.selectIssue);
  const { data: issuesData, isLoading: issuesLoading } = useIssuesQuery(projectId);
  const { data, isLoading } = useScriptWorkspaceQuery(projectId);
  const { data: aiProviders } = useAIProvidersQuery();
  const generateScript = useGenerateScriptMutation(projectId);
  const regenerateSection = useRegenerateScriptSectionMutation(projectId);
  const [selectedIssueId, setSelectedIssueId] = useState("");

  const selectedProvider = stageProvider || aiProviders?.defaults.script || "openai";
  const selectedMode = (() => {
    const stageState = aiProviders?.items
      .find((provider) => provider.id === selectedProvider)
      ?.stages.find((stage) => stage.stage === "script");
    if (!stageState) return "mock";
    return stageState.real_available ? stageState.default_mode : "mock";
  })();
  const selectedIssue = issuesData?.items.find((item) => item.id === selectedIssueId) ?? issuesData?.items[0];

  useEffect(() => {
    if (storedSelectedIssueId && issuesData?.items.some((item) => item.id === storedSelectedIssueId)) {
      setSelectedIssueId(storedSelectedIssueId);
      return;
    }
    if (!selectedIssueId && issuesData?.items[0]?.id) {
      setSelectedIssueId(issuesData.items[0].id);
    }
  }, [issuesData, selectedIssueId, storedSelectedIssueId]);

  useEffect(() => {
    if (!stageProvider && aiProviders?.defaults.script) {
      setStageProvider("scripts", aiProviders.defaults.script);
    }
  }, [aiProviders, setStageProvider, stageProvider]);

  const firstSection = data?.sections[0];
  const lastSection = data?.sections[data.sections.length - 1];
  const headerActions = [
    {
      label: generateScript.isPending ? "전체 생성 중..." : "전체 재생성",
      variant: "primary" as const,
      onClick: (): void => {
        void generateScript.mutateAsync({
          project_id: projectId,
          issue_id: selectedIssue?.id ?? "",
          issue_summary: selectedIssue ? `${selectedIssue.title} 관련 핵심 흐름을 정리합니다.` : "",
          user_instructions: stageInstruction,
          style_preset: "설명형",
          audience_type: "대중",
          tone: "차분한 분석형",
          provider_id: selectedProvider,
          provider_mode: selectedMode
        });
      },
      disabled: generateScript.isPending || !selectedIssue?.id
    },
    {
      label: regenerateSection.isPending ? "도입 재생성 중..." : "도입만 재생성",
      variant: "secondary" as const,
      onClick: (): void => {
        if (!firstSection) return;
        void regenerateSection.mutateAsync({
          project_id: projectId,
          script_id: data?.scriptId ?? "",
          section_id: firstSection.id,
          user_instructions: stageInstruction,
          provider_id: selectedProvider,
          provider_mode: selectedMode
        });
      },
      disabled: regenerateSection.isPending || !data?.scriptId || !firstSection
    },
    {
      label: regenerateSection.isPending ? "결론 재생성 중..." : "결론만 재생성",
      variant: "secondary" as const,
      onClick: (): void => {
        if (!lastSection) return;
        void regenerateSection.mutateAsync({
          project_id: projectId,
          script_id: data?.scriptId ?? "",
          section_id: lastSection.id,
          user_instructions: stageInstruction,
          provider_id: selectedProvider,
          provider_mode: selectedMode
        });
      },
      disabled: regenerateSection.isPending || !data?.scriptId || !lastSection
    }
  ];

  if (isLoading || issuesLoading || !data || !issuesData) {
    return <LoadingPanel label="대본 작업 공간을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="5단계"
        title="대본 생성"
        description="선택한 이슈, 검증된 통계, 시장 보조 자료, 사용자 지시를 바탕으로 10분 분량 한국어 대본을 생성합니다."
        actions={headerActions}
      />

      <div className="mb-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-4">
          <p className="text-sm font-semibold text-ink">기준 이슈 선택</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            현재 프로젝트 이슈 중 하나를 선택하고, 선택한 AI의 기본 모드에 맞춰 생성 흐름을 검증할 수 있습니다.
          </p>
          <Select
            className="mt-4"
            value={selectedIssueId}
            onChange={(event) => {
              setSelectedIssueId(event.target.value);
              selectIssue(event.target.value);
            }}
          >
            {issuesData.items.map((item) => (
              <option key={item.id} value={item.id}>
                {item.title}
              </option>
            ))}
          </Select>
        </div>

        <AIProviderSelector
          stage="script"
          value={selectedProvider}
          catalog={aiProviders}
          onChange={(providerId) => setStageProvider("scripts", providerId)}
        />
      </div>

      {generateScript.isError || regenerateSection.isError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {(generateScript.error ?? regenerateSection.error) instanceof Error
            ? (generateScript.error ?? regenerateSection.error)?.message
            : "대본 생성 중 오류가 발생했습니다."}
        </div>
      ) : null}

      <div className="panel-grid panel-grid-3">
        <SectionCard
          title={data.scriptId ? data.title : "대본 편집기"}
          description={data.scriptId ? data.summary : "먼저 대본 생성 버튼을 눌러 장면과 근거 매핑을 만드세요."}
        >
          <div className="space-y-5">
            {data.sections.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-slate-300 p-6 text-sm leading-6 text-slate-500">
                아직 생성된 대본이 없습니다. 이슈 선택 후 상단의 `전체 재생성` 버튼으로 mock 생성부터 시작해보세요.
              </div>
            ) : null}
            {data.sections.map((section) => (
              <div key={section.id} className="rounded-3xl border border-slate-200 p-5">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-lg font-semibold text-ink">{section.heading}</h3>
                  <span className="text-xs text-slate-500">
                    {data.providerName} · {data.providerMode}
                  </span>
                </div>
                <Textarea className="mt-4 min-h-40" value={section.content} readOnly />
                <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                  {section.evidences.map((evidence) => (
                    <span key={evidence} className="rounded-full bg-slate-100 px-3 py-1">
                      {evidence}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="근거 매핑" description="숫자 문장과 연결된 근거를 즉시 검토할 수 있는 패널입니다.">
          <EvidencePanel items={data.evidences} />
        </SectionCard>

        <InstructionPanel stageKey="scripts" title="대본 생성 지시" />
      </div>
    </>
  );
}
