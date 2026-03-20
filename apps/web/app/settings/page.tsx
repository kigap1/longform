"use client";

import { useEffect, useMemo, useState } from "react";

import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs } from "@/components/ui/tabs";
import { useAIProvidersQuery, useSaveSettingsMutation, useSettingsQuery } from "@/lib/api/hooks";


function fieldId(category: string, key: string) {
  return `${category}:${key}`;
}

export default function SettingsPage() {
  const { data, isLoading } = useSettingsQuery();
  const { data: aiProviders } = useAIProvidersQuery();
  const saveSettings = useSaveSettingsMutation();
  const [activeTab, setActiveTab] = useState("API");
  const [draftValues, setDraftValues] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState<string>("");

  useEffect(() => {
    if (!data) return;
    setActiveTab((current) => (data.tabs.includes(current) ? current : data.tabs[0] ?? "API"));
    setDraftValues(
      Object.fromEntries(
        data.sections.flatMap((section) =>
          section.fields.map((field) => [fieldId(section.category, field.key), field.value])
        )
      )
    );
  }, [data]);

  const activeSections = useMemo(() => {
    if (!data) return [];
    return data.sections
      .filter((section) => section.tab === activeTab)
      .map((section) => ({
        ...section,
        fields: section.fields.map((field) => ({
          ...field,
          value: draftValues[fieldId(section.category, field.key)] ?? field.value
        }))
      }));
  }, [activeTab, data, draftValues]);

  if (isLoading || !data) {
    return <LoadingPanel label="설정 폼을 불러오는 중입니다..." />;
  }

  async function handleSave() {
    const payload = activeSections.flatMap((section) =>
      section.fields.map((field) => ({
        category: section.category,
        key: field.key,
        value: draftValues[fieldId(section.category, field.key)] ?? field.value,
        secret: field.secret
      }))
    );
    await saveSettings.mutateAsync(payload);
    setFeedback("현재 탭 설정을 저장했습니다.");
  }

  return (
    <>
      <PageHeader
        eyebrow="운영 설정"
        title="설정"
        description="모델 기본값, 통계 제공자 키, 저장소 모드, 신선도 기준, 출력 경로를 프로젝트 전반에 걸쳐 관리합니다."
      />

      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <Tabs items={data.tabs} value={activeTab} onChange={setActiveTab} />
        <Button onClick={handleSave} disabled={saveSettings.isPending}>
          {saveSettings.isPending ? "저장 중..." : "현재 탭 저장"}
        </Button>
      </div>

      <div className="mb-6 rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-700">
        AI 키와 기본 공급자 관리는 사이드바의 `AI 연결` 메뉴에서 더 집중적으로 다룰 수 있습니다.
      </div>

      {activeTab === "API" && aiProviders ? (
        <div className="mb-6 grid gap-4 xl:grid-cols-3">
          {aiProviders.items.map((provider) => (
            <div key={provider.id} className="rounded-[24px] border border-slate-200 bg-white p-5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-lg font-semibold text-ink">{provider.label}</h2>
                <Badge tone={provider.configured ? "success" : "default"}>
                  {provider.configured ? "일부 설정됨" : "미설정"}
                </Badge>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-500">{provider.description}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {provider.stages.map((stage) => (
                  <Badge
                    key={`${provider.id}-${stage.stage}`}
                    tone={stage.supported ? (stage.real_available ? "success" : "warning") : "default"}
                  >
                    {stage.stage === "script" ? "대본" : stage.stage === "image" ? "이미지" : "비디오"} ·{" "}
                    {stage.supported ? (stage.real_available ? "실연동 준비" : "mock 우선") : "미지원"}
                  </Badge>
                ))}
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-500">
                기본 선택 단계:
                {" "}
                {provider.stages
                  .filter((stage) => stage.default_selected)
                  .map((stage) => (stage.stage === "script" ? "대본" : stage.stage === "image" ? "이미지" : "비디오"))
                  .join(", ") || "없음"}
              </p>
            </div>
          ))}
        </div>
      ) : null}

      {feedback ? (
        <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {feedback}
        </div>
      ) : null}

      {saveSettings.isError ? (
        <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {saveSettings.error instanceof Error ? saveSettings.error.message : "설정 저장 중 오류가 발생했습니다."}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-2">
        {activeSections.map((section) => (
          <SectionCard
            key={section.title}
            title={section.title}
            description="mock 모드에서는 로컬 상태만 유지하고, real 모드에서는 FastAPI 설정 저장 엔드포인트와 연결됩니다."
          >
            <div className="space-y-4">
              {section.fields.map((field) => (
                <div key={fieldId(section.category, field.key)} className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">{field.label}</label>
                  <Input
                    type={field.secret ? "password" : "text"}
                    value={field.value}
                    placeholder={field.placeholder}
                    onChange={(event) =>
                      setDraftValues((current) => ({
                        ...current,
                        [fieldId(section.category, field.key)]: event.target.value
                      }))
                    }
                  />
                </div>
              ))}
              <Button variant="secondary" onClick={handleSave} disabled={saveSettings.isPending}>
                {saveSettings.isPending ? "저장 중..." : "프로젝트 기본값에 적용"}
              </Button>
            </div>
          </SectionCard>
        ))}
      </div>
    </>
  );
}
