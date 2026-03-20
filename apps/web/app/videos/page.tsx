"use client";

import { useEffect, useState } from "react";

import { AIProviderSelector } from "@/components/shared/ai-provider-selector";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { useAIProvidersQuery, useExecuteVideosMutation, usePrepareVideosMutation, useVideoWorkspaceQuery } from "@/lib/api/hooks";
import type { VideoExecutionResult, VideoPreparationResult } from "@/lib/api/types";
import { useProjectStore } from "@/lib/stores/project-store";


export default function VideosPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const stageInstruction = useProjectStore((state) => state.stageInstructions.videos ?? "");
  const stageProvider = useProjectStore((state) => state.stageProviders.videos ?? "");
  const setStageProvider = useProjectStore((state) => state.setStageProvider);
  const { data, isLoading } = useVideoWorkspaceQuery(projectId);
  const { data: aiProviders } = useAIProvidersQuery();
  const prepareVideos = usePrepareVideosMutation(projectId);
  const executeVideos = useExecuteVideosMutation(projectId);
  const [prepared, setPrepared] = useState<VideoPreparationResult[]>([]);
  const [executions, setExecutions] = useState<Record<string, VideoExecutionResult>>({});

  const selectedProvider = stageProvider || aiProviders?.defaults.video || "openai";
  const selectedMode = (() => {
    const stageState = aiProviders?.items
      .find((provider) => provider.id === selectedProvider)
      ?.stages.find((stage) => stage.stage === "video");
    if (!stageState) return "mock";
    return stageState.real_available ? stageState.default_mode : "mock";
  })();
  const sceneIds = data?.scenes.map((scene) => scene.id) ?? [];

  useEffect(() => {
    if (!stageProvider && aiProviders?.defaults.video) {
      setStageProvider("videos", aiProviders.defaults.video);
    }
  }, [aiProviders, setStageProvider, stageProvider]);

  async function handlePrepare() {
    const result = await prepareVideos.mutateAsync({
      project_id: projectId,
      scene_ids: sceneIds,
      user_instructions: stageInstruction,
      provider_id: selectedProvider,
      provider_mode: selectedMode
    });
    setPrepared(result);
  }

  async function handleExecute() {
    if (!prepared.length) return;
    const result = await executeVideos.mutateAsync({
      project_id: projectId,
      video_asset_ids: prepared.map((item) => item.id),
      user_instructions: stageInstruction,
      provider_id: selectedProvider,
      provider_mode: selectedMode
    });
    setExecutions(Object.fromEntries(result.map((item) => [item.videoAssetId, item])));
  }

  const actions = [
    {
      label: prepareVideos.isPending ? "번들 준비 중..." : "번들 준비",
      variant: "primary" as const,
      onClick: (): void => {
        void handlePrepare();
      },
      disabled: prepareVideos.isPending || sceneIds.length === 0
    },
    {
      label: executeVideos.isPending ? "실행 중..." : selectedMode === "real" ? "real 실행" : "mock 실행",
      variant: "secondary" as const,
      onClick: (): void => {
        void handleExecute();
      },
      disabled: executeVideos.isPending || prepared.length === 0
    }
  ];

  if (isLoading || !data) {
    return <LoadingPanel label="영상 준비 장면을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="8단계"
        title="영상 생성"
        description="Veo 계열 워크플로 또는 Kling AI 브리지로 넘길 장면별 모션 지시, 프롬프트, 번들 구성을 준비합니다."
        actions={actions}
      />

      <div className="mb-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-4">
          <p className="text-sm font-semibold text-ink">번들 대상 scene</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            최신 대본 scene 전체를 대상으로 번들을 생성합니다. 이미지가 있으면 최신 이미지를 자동으로 포함합니다.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {data.scenes.map((scene) => (
              <span key={scene.id} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                {scene.title}
              </span>
            ))}
          </div>
        </div>

        <AIProviderSelector
          stage="video"
          value={selectedProvider}
          catalog={aiProviders}
          onChange={(providerId) => setStageProvider("videos", providerId)}
        />
      </div>

      {prepareVideos.isError || executeVideos.isError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {(prepareVideos.error ?? executeVideos.error) instanceof Error
            ? (prepareVideos.error ?? executeVideos.error)?.message
            : "비디오 준비 중 오류가 발생했습니다."}
        </div>
      ) : null}

      <div className="panel-grid panel-grid-3">
        <SectionCard title="장면별 모션 설계" description="장면 순서, 카메라 움직임, 자막 타이밍을 함께 정의합니다.">
          <div className="space-y-4">
            {data.scenes.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-slate-300 p-6 text-sm leading-6 text-slate-500">
                준비할 scene이 없습니다. 먼저 대본과 이미지 단계를 진행하세요.
              </div>
            ) : null}

            {data.scenes.map((scene) => {
              const preparedAsset = prepared.find((item) => item.sceneId === scene.id);
              const executed = preparedAsset ? executions[preparedAsset.id] : undefined;
              return (
                <div key={scene.id} className="rounded-3xl border border-slate-200 p-5">
                  <h3 className="text-lg font-semibold text-ink">{scene.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{scene.description}</p>
                  <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">{scene.motion}</div>
                  {preparedAsset ? (
                    <div className="mt-4 rounded-2xl border border-slate-200 p-4 text-sm text-slate-600">
                      <p className="font-medium text-ink">
                        {preparedAsset.providerName} · {preparedAsset.providerMode} · {preparedAsset.status}
                      </p>
                      <p className="mt-2 break-all">번들: {preparedAsset.bundlePath}</p>
                      {executed ? <p className="mt-2 break-all">실행 결과: {executed.outputPath}</p> : null}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        </SectionCard>

        <SectionCard title="번들 내보내기 규칙" description="프롬프트, 참조 이미지, 장면 메타데이터를 세트로 묶어 전달합니다.">
          <div className="space-y-3 text-sm leading-6 text-slate-600">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">포함 항목</p>
              <p className="mt-2">장면 프롬프트, 모션 지시, 참조 이미지, 캐릭터 잠금 규칙, 근거 요약</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">현재 테스트 범위</p>
              <p className="mt-2">OpenAI, Gemini, Kling mock 경로를 먼저 검증할 수 있고, Claude는 비디오 단계에서 비활성화했습니다.</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="videos" title="영상 준비 지시" />
      </div>
    </>
  );
}
