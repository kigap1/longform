"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

import { AIProviderSelector } from "@/components/shared/ai-provider-selector";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useAIProvidersQuery, useGenerateImageMutation, useImageWorkspaceQuery, useRegenerateImageMutation } from "@/lib/api/hooks";
import type { ImageGenerationResult } from "@/lib/api/types";
import { useProjectStore } from "@/lib/stores/project-store";


export default function ImagesPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const stageInstruction = useProjectStore((state) => state.stageInstructions.images ?? "");
  const stageProvider = useProjectStore((state) => state.stageProviders.images ?? "");
  const setStageProvider = useProjectStore((state) => state.setStageProvider);
  const { data, isLoading } = useImageWorkspaceQuery(projectId);
  const { data: aiProviders } = useAIProvidersQuery();
  const generateImage = useGenerateImageMutation(projectId);
  const regenerateImage = useRegenerateImageMutation(projectId);
  const [selectedSceneId, setSelectedSceneId] = useState("");
  const [draftPrompts, setDraftPrompts] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, ImageGenerationResult>>({});
  const [isBatchGenerating, setIsBatchGenerating] = useState(false);

  const selectedProvider = stageProvider || aiProviders?.defaults.image || "openai";
  const selectedMode = (() => {
    const stageState = aiProviders?.items
      .find((provider) => provider.id === selectedProvider)
      ?.stages.find((stage) => stage.stage === "image");
    if (!stageState) return "mock";
    return stageState.real_available ? stageState.default_mode : "mock";
  })();
  const selectedScene = data?.scenes.find((scene) => scene.id === selectedSceneId) ?? data?.scenes[0];

  useEffect(() => {
    if (!selectedSceneId && data?.scenes[0]?.id) {
      setSelectedSceneId(data.scenes[0].id);
    }
  }, [data, selectedSceneId]);

  useEffect(() => {
    if (!stageProvider && aiProviders?.defaults.image) {
      setStageProvider("images", aiProviders.defaults.image);
    }
  }, [aiProviders, setStageProvider, stageProvider]);

  useEffect(() => {
    if (!data) return;
    setDraftPrompts((current) => ({
      ...Object.fromEntries(data.scenes.map((scene) => [scene.id, scene.prompt])),
      ...current
    }));
  }, [data]);

  async function handleGenerateAll() {
    if (!data?.scenes.length) return;
    setIsBatchGenerating(true);
    try {
      for (const scene of data.scenes) {
        const result = await generateImage.mutateAsync({
          project_id: projectId,
          scene_id: scene.id,
          prompt_override: draftPrompts[scene.id] ?? scene.prompt,
          user_instructions: stageInstruction,
          provider_id: selectedProvider,
          provider_mode: selectedMode
        });
        setResults((current) => ({ ...current, [scene.id]: result }));
      }
    } finally {
      setIsBatchGenerating(false);
    }
  }

  async function handleRegenerateSelected() {
    if (!selectedScene) return;
    const result = await regenerateImage.mutateAsync({
      project_id: projectId,
      scene_id: selectedScene.id,
      prompt_override: draftPrompts[selectedScene.id] ?? selectedScene.prompt,
      user_instructions: stageInstruction,
      provider_id: selectedProvider,
      provider_mode: selectedMode
    });
    setResults((current) => ({ ...current, [selectedScene.id]: result }));
  }

  const actions = [
    {
      label: isBatchGenerating ? "일괄 생성 중..." : "일괄 생성",
      variant: "primary" as const,
      onClick: (): void => {
        void handleGenerateAll();
      },
      disabled: isBatchGenerating || !data?.scenes.length
    },
    {
      label: regenerateImage.isPending ? "선택 장면 재생성 중..." : "선택 장면 재생성",
      variant: "secondary" as const,
      onClick: (): void => {
        void handleRegenerateSelected();
      },
      disabled: regenerateImage.isPending || !selectedScene
    }
  ];

  if (isLoading || !data) {
    return <LoadingPanel label="이미지 장면 구성을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="7단계"
        title="이미지 생성"
        description="한국어 인포그래픽 스타일 장면 이미지를 생성하고, 장면별 프롬프트를 직접 수정하거나 재생성할 수 있습니다."
        actions={actions}
      />

      <div className="mb-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-4">
          <p className="text-sm font-semibold text-ink">장면 선택</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            최신 대본의 scene 목록을 사용합니다. scene이 없다면 먼저 대본 생성을 실행하세요.
          </p>
          <Select className="mt-4" value={selectedSceneId} onChange={(event) => setSelectedSceneId(event.target.value)}>
            {data.scenes.map((scene) => (
              <option key={scene.id} value={scene.id}>
                {scene.title}
              </option>
            ))}
          </Select>
        </div>

        <AIProviderSelector
          stage="image"
          value={selectedProvider}
          catalog={aiProviders}
          onChange={(providerId) => setStageProvider("images", providerId)}
        />
      </div>

      {generateImage.isError || regenerateImage.isError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {(generateImage.error ?? regenerateImage.error) instanceof Error
            ? (generateImage.error ?? regenerateImage.error)?.message
            : "이미지 생성 중 오류가 발생했습니다."}
        </div>
      ) : null}

      <div className="panel-grid panel-grid-3">
        <SectionCard title="장면별 프롬프트 편집" description="동일 캐릭터를 유지하면서도 장면 목적에 맞게 프롬프트를 조정합니다.">
          <div className="space-y-5">
            {data.scenes.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-slate-300 p-6 text-sm leading-6 text-slate-500">
                아직 이미지로 넘길 scene이 없습니다. 먼저 대본 생성 단계에서 scene을 만든 뒤 다시 들어오세요.
              </div>
            ) : null}

            {data.scenes.map((scene) => {
              const generated = results[scene.id];
              const active = scene.id === selectedSceneId;
              return (
                <div
                  key={scene.id}
                  className={`rounded-3xl border p-5 ${active ? "border-teal-500 bg-teal-50/40" : "border-slate-200"}`}
                >
                  <div className="grid gap-5 lg:grid-cols-[180px_1fr]">
                    {generated?.assetUrl ? (
                      <Image
                        className="aspect-[3/4] rounded-[24px] border border-slate-200 object-cover"
                        src={generated.assetUrl}
                        alt={scene.title}
                        width={720}
                        height={960}
                        unoptimized
                      />
                    ) : (
                      <button
                        type="button"
                        className="aspect-[3/4] rounded-[24px] bg-[linear-gradient(180deg,#112240,#0f766e)]"
                        onClick={() => setSelectedSceneId(scene.id)}
                      />
                    )}
                    <div>
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <h3 className="text-lg font-semibold text-ink">{scene.title}</h3>
                          <p className="mt-1 text-sm text-slate-500">{scene.description}</p>
                        </div>
                        <Button variant="secondary" onClick={() => setSelectedSceneId(scene.id)}>
                          선택
                        </Button>
                      </div>
                      <Textarea
                        className="mt-4 min-h-28"
                        value={draftPrompts[scene.id] ?? scene.prompt}
                        onChange={(event) =>
                          setDraftPrompts((current) => ({
                            ...current,
                            [scene.id]: event.target.value
                          }))
                        }
                      />
                      {generated ? (
                        <p className="mt-3 text-xs text-slate-500">
                          최근 생성: {generated.providerName} · {generated.providerMode} · {generated.status}
                        </p>
                      ) : null}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </SectionCard>

        <SectionCard title="생성 기준" description="인포그래픽 가독성과 한국어 텍스트 레이아웃을 우선합니다.">
          <div className="space-y-3 text-sm leading-6 text-slate-600">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">필수 조건</p>
              <p className="mt-2">세로형 우선, 한국어 텍스트 포함, 숫자 강조 박스, 진행자 캐릭터 유지</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">현재 테스트 범위</p>
              <p className="mt-2">OpenAI/Gemini mock 경로 우선, Claude는 이미지 단계에서 비활성화했습니다.</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="images" title="이미지 생성 지시" />
      </div>
    </>
  );
}
