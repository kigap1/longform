"use client";

import { EvidencePanel } from "@/components/shared/evidence-panel";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useScriptsQuery } from "@/lib/api/hooks";


export default function ScriptsPage() {
  const { data, isLoading } = useScriptsQuery();

  if (isLoading || !data) {
    return <LoadingPanel label="대본 작업 공간을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="5단계"
        title="대본 생성"
        description="선택한 이슈, 검증된 통계, 시장 보조 자료, 사용자 지시를 바탕으로 10분 분량 한국어 대본을 생성합니다."
        actions={[
          { label: "전체 재생성", variant: "primary" },
          { label: "도입만 재생성", variant: "secondary" },
          { label: "결론만 재생성", variant: "secondary" }
        ]}
      />

      <div className="panel-grid panel-grid-3">
        <SectionCard title="대본 편집기" description="문단별 수정과 재생성을 병행할 수 있도록 섹션 단위 편집 구조를 둡니다.">
          <div className="space-y-5">
            {data.sections.map((section) => (
              <div key={section.heading} className="rounded-3xl border border-slate-200 p-5">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-lg font-semibold text-ink">{section.heading}</h3>
                  <div className="flex gap-2">
                    <Button variant="secondary">섹션 재생성</Button>
                    <Button variant="ghost">근거 보기</Button>
                  </div>
                </div>
                <Textarea className="mt-4 min-h-40" defaultValue={section.content} />
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
