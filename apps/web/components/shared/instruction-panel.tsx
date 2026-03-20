"use client";

import { useProjectStore } from "@/lib/stores/project-store";
import { Textarea } from "@/components/ui/textarea";


type InstructionPanelProps = {
  stageKey: string;
  title?: string;
};

export function InstructionPanel({ stageKey, title = "추가 지시" }: InstructionPanelProps) {
  const value = useProjectStore((state) => state.stageInstructions[stageKey] ?? "");
  const setStageInstruction = useProjectStore((state) => state.setStageInstruction);

  return (
    <div className="rounded-[24px] border border-dashed border-slate-300 bg-slate-50/70 p-4">
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      <p className="mt-2 text-sm leading-6 text-slate-500">
        각 단계별로 수동 지시를 추가해 생성 결과를 세밀하게 조정할 수 있습니다.
      </p>
      <Textarea
        className="mt-4 bg-white"
        placeholder="예: 수치는 공식 통계만 사용하고, 결론은 투자 조언으로 오해되지 않게 작성"
        value={value}
        onChange={(event) => setStageInstruction(stageKey, event.target.value)}
      />
    </div>
  );
}

