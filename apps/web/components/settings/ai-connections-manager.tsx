"use client";

import { useEffect, useMemo, useState } from "react";

import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useAIProvidersQuery, useSaveSettingsMutation, useSettingsQuery } from "@/lib/api/hooks";


function fieldId(key: string) {
  return `api:${key}`;
}

function stageLabel(stage: "script" | "image" | "video") {
  if (stage === "script") return "대본";
  if (stage === "image") return "이미지";
  return "비디오";
}

const stageDefaultFields = [
  { key: "script_default_provider", stage: "script" as const, label: "대본 기본 AI" },
  { key: "image_default_provider", stage: "image" as const, label: "이미지 기본 AI" },
  { key: "video_default_provider", stage: "video" as const, label: "비디오 기본 AI" }
];

const stageModeFields = [
  { key: "script_provider_mode", stage: "script" as const, label: "대본 기본 모드" },
  { key: "image_provider_mode", stage: "image" as const, label: "이미지 기본 모드" },
  { key: "video_provider_mode", stage: "video" as const, label: "비디오 기본 모드" }
];

export function AIConnectionsManager() {
  const { data: settings, isLoading } = useSettingsQuery();
  const { data: catalog } = useAIProvidersQuery();
  const saveSettings = useSaveSettingsMutation();
  const [draftValues, setDraftValues] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState("");

  useEffect(() => {
    if (!settings) return;
    setDraftValues(
      Object.fromEntries(
        settings.sections.flatMap((section) => section.fields.map((field) => [fieldId(field.key), field.value]))
      )
    );
  }, [settings]);

  const fieldMeta = useMemo(() => {
    const fields = new Map<string, { secret: boolean }>();
    (catalog?.items ?? []).forEach((provider) => {
      provider.fields.forEach((field) => {
        fields.set(field.key, { secret: !!field.secret });
      });
    });
    return fields;
  }, [catalog]);

  if (isLoading || !settings || !catalog) {
    return <LoadingPanel label="AI 연결 설정을 불러오는 중입니다..." />;
  }

  function updateValue(key: string, value: string) {
    setDraftValues((current) => ({
      ...current,
      [fieldId(key)]: value
    }));
  }

  async function saveKeys(keys: readonly string[], message: string) {
    await saveSettings.mutateAsync(
      keys.map((key) => ({
        category: "api",
        key,
        value: draftValues[fieldId(key)] ?? "",
        secret: fieldMeta.get(key)?.secret ?? false
      }))
    );
    setFeedback(message);
  }

  return (
    <>
      <PageHeader
        eyebrow="AI 운영"
        title="AI 연결"
        description="OpenAI, Claude, Gemini 순서를 유지하고 비디오 단계에 Kling AI를 추가했습니다. 키, 기본 공급자, mock/real 모드를 GUI에서 저장할 수 있습니다."
      />

      <div className="mb-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-5">
          <p className="text-sm font-semibold text-ink">저장 방식</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            여기서 저장한 값은 FastAPI 설정 테이블에 바로 반영됩니다. 생성 화면에서는 단계별로 공급자를 다시 고를 수 있고, 기본값은 여기서 관리합니다.
          </p>
        </div>
        <div className="rounded-[24px] border border-slate-200 bg-white p-5">
          <p className="text-sm font-semibold text-ink">Kling 경계</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Kling base URL 기본값은 공식 글로벌 웹앱에서 확인된 값을 넣어두었습니다. submit/status/result 경로는 공식 또는 사내 브리지에 맞춰 직접 입력해야 합니다.
          </p>
        </div>
      </div>

      {feedback ? (
        <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {feedback}
        </div>
      ) : null}

      {saveSettings.isError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {saveSettings.error instanceof Error ? saveSettings.error.message : "AI 연결 설정 저장 중 오류가 발생했습니다."}
        </div>
      ) : null}

      <div className="mb-6">
        <SectionCard title="기본 공급자와 모드" description="각 단계에서 처음 선택될 AI와 기본 실행 모드를 여기서 정합니다.">
          <div className="grid gap-4 md:grid-cols-3">
            {stageDefaultFields.map((item) => {
              const selectedProvider = draftValues[fieldId(item.key)] || catalog.defaults[item.stage] || "openai";
              const support = catalog.items
                .find((provider) => provider.id === selectedProvider)
                ?.stages.find((stage) => stage.stage === item.stage);
              return (
                <div key={item.key} className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">{item.label}</label>
                  <Select value={selectedProvider} onChange={(event) => updateValue(item.key, event.target.value)}>
                    {catalog.items
                      .filter((provider) => provider.stages.some((stage) => stage.stage === item.stage && stage.supported))
                      .map((provider) => (
                        <option key={provider.id} value={provider.id}>
                          {provider.label}
                        </option>
                      ))}
                  </Select>
                  {support ? <p className="text-xs leading-5 text-slate-500">{support.note}</p> : null}
                </div>
              );
            })}
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {stageModeFields.map((item) => {
              const defaultProviderKey = stageDefaultFields.find((field) => field.stage === item.stage)?.key ?? "";
              const selectedProvider = draftValues[fieldId(defaultProviderKey)] || catalog.defaults[item.stage] || "openai";
              const support = catalog.items
                .find((provider) => provider.id === selectedProvider)
                ?.stages.find((stage) => stage.stage === item.stage);
              const currentMode = draftValues[fieldId(item.key)] || support?.default_mode || "mock";
              const allowReal = !!support?.real_available;
              return (
                <div key={item.key} className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">{item.label}</label>
                  <Select value={currentMode} onChange={(event) => updateValue(item.key, event.target.value)}>
                    <option value="mock">mock</option>
                    <option value="real" disabled={!allowReal}>
                      real
                    </option>
                  </Select>
                  <p className="text-xs leading-5 text-slate-500">
                    {allowReal ? "real 선택 가능" : "현재 선택된 공급자는 mock 모드 우선"}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="mt-5">
            <Button
              onClick={() =>
                void saveKeys(
                  [...stageDefaultFields.map((item) => item.key), ...stageModeFields.map((item) => item.key)],
                  "기본 공급자와 모드를 저장했습니다."
                )
              }
              disabled={saveSettings.isPending}
            >
              {saveSettings.isPending ? "저장 중..." : "기본값 저장"}
            </Button>
          </div>
        </SectionCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        {catalog.items.map((provider) => (
          <SectionCard
            key={provider.id}
            title={provider.label}
            description={provider.description}
          >
            <div className="flex flex-wrap gap-2">
              <Badge tone={provider.configured ? "success" : "default"}>
                {provider.configured ? "일부 설정됨" : "미설정"}
              </Badge>
              {provider.stages.map((stage) => (
                <Badge
                  key={`${provider.id}-${stage.stage}`}
                  tone={stage.supported ? (stage.real_available ? "success" : "warning") : "default"}
                >
                  {stageLabel(stage.stage)} · {stage.supported ? (stage.real_available ? "실연동 경계" : "mock 우선") : "미지원"}
                </Badge>
              ))}
            </div>

            <div className="mt-5 space-y-4">
              {provider.fields.map((field) => (
                <div key={field.key} className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">{field.label}</label>
                  <Input
                    type={field.secret ? "password" : "text"}
                    value={draftValues[fieldId(field.key)] ?? ""}
                    placeholder={field.placeholder}
                    onChange={(event) => updateValue(field.key, event.target.value)}
                  />
                </div>
              ))}
            </div>

            <div className="mt-5 space-y-2">
              {provider.stages.map((stage) => (
                <p key={`${provider.id}-${stage.stage}-note`} className="text-xs leading-5 text-slate-500">
                  {stageLabel(stage.stage)}: {stage.note}
                </p>
              ))}
            </div>

            <div className="mt-5">
              <Button
                variant="secondary"
                onClick={() =>
                  void saveKeys(
                    provider.fields.map((field) => field.key),
                    `${provider.label} 연결 설정을 저장했습니다.`
                  )
                }
                disabled={saveSettings.isPending}
              >
                {saveSettings.isPending ? "저장 중..." : `${provider.label} 저장`}
              </Button>
            </div>
          </SectionCard>
        ))}
      </div>
    </>
  );
}
