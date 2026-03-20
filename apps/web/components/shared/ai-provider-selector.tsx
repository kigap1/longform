"use client";

import type { AIProviderCatalog } from "@/lib/api/types";
import { Select } from "@/components/ui/select";


type AIProviderSelectorProps = {
  stage: "script" | "image" | "video";
  value: string;
  catalog?: AIProviderCatalog;
  onChange: (value: string) => void;
};

export function AIProviderSelector({ stage, value, catalog, onChange }: AIProviderSelectorProps) {
  const providers = [...(catalog?.items ?? [])].sort((left, right) => left.order - right.order);
  const current = providers.find((provider) => provider.id === value);
  const stageState = current?.stages.find((item) => item.stage === stage);

  return (
    <div className="rounded-[24px] border border-slate-200 bg-white p-4">
      <p className="text-sm font-semibold text-ink">생성 AI 선택</p>
      <p className="mt-2 text-sm leading-6 text-slate-500">
        OpenAI, Claude, Gemini 순서를 유지하고 Kling AI를 뒤에 추가했습니다. 현재 단계에서 지원되지 않는 공급자는 비활성화했습니다.
      </p>
      <Select className="mt-4" value={value} onChange={(event) => onChange(event.target.value)}>
        {providers.map((provider) => {
          const support = provider.stages.find((item) => item.stage === stage);
          const disabled = !support?.supported;
          const suffix = disabled ? " (준비 중)" : !support?.real_available ? " (mock 테스트)" : "";
          return (
            <option key={provider.id} value={provider.id} disabled={disabled}>
              {provider.label}
              {suffix}
            </option>
          );
        })}
      </Select>
      {stageState ? <p className="mt-3 text-xs leading-5 text-slate-500">{stageState.note}</p> : null}
    </div>
  );
}
