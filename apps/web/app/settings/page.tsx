"use client";

import { useEffect, useMemo, useState } from "react";

import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs } from "@/components/ui/tabs";
import { useSaveSettingsMutation, useSettingsQuery } from "@/lib/api/hooks";


function fieldId(category: string, key: string) {
  return `${category}:${key}`;
}

export default function SettingsPage() {
  const { data, isLoading } = useSettingsQuery();
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
