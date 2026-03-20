"use client";

import { useMemo, useState } from "react";

import { FilterBar } from "@/components/shared/filter-bar";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useIssuesQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function IssuesPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const { data, isLoading } = useIssuesQuery(projectId);
  const [activeFilter, setActiveFilter] = useState("전체");

  const filteredItems = useMemo(() => {
    if (!data) return [];
    if (activeFilter === "전체") return data.items;
    return data.items.filter((item) => item.category === activeFilter);
  }, [data, activeFilter]);

  if (isLoading || !data) {
    return <LoadingPanel label="이슈 탐색 화면을 준비하는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="1단계"
        title="이슈 탐색"
        description="국내외 기사 군집, 중복 제거, 우선순위 점수와 랭킹 근거를 함께 보여주는 단계입니다."
        actions={[{ label: "랭킹 다시 계산", variant: "primary" }, { label: "기사 수집 시작", variant: "secondary" }]}
      />

      <div className="mb-6">
        <FilterBar title="이슈 분류 필터" options={data.filters} value={activeFilter} onChange={setActiveFilter} />
      </div>

      <div className="panel-grid panel-grid-3">
        <SectionCard title="랭킹 카드" description="최근성, 기사 빈도, 출처 신뢰도, 시장 영향도를 종합 반영합니다.">
          <div className="space-y-4">
            {filteredItems.map((issue) => (
              <div key={issue.id} className="rounded-3xl border border-slate-200 bg-slate-50/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm text-slate-500">{issue.category}</p>
                    <h3 className="mt-1 text-lg font-semibold text-ink">{issue.title}</h3>
                  </div>
                  <Badge tone="success">우선 {issue.score.toFixed(2)}</Badge>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {issue.reasons.map((reason) => (
                    <Badge key={reason}>{reason}</Badge>
                  ))}
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="secondary">관련 기사 보기</Button>
                  <Button variant="ghost">프로젝트 이슈로 채택</Button>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="관련 기사 그룹" description="중복 기사 묶음을 편집하고 제외할 수 있는 영역입니다.">
          <div className="space-y-3 text-sm text-slate-600">
            {data.groups.map((group) => (
              <div key={group.title} className="rounded-2xl border border-slate-200 p-4">
                <p className="font-medium text-ink">{group.title}</p>
                <p className="mt-2 leading-6">{group.detail}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <InstructionPanel stageKey="issues" title="이슈 탐색 지시" />
      </div>
    </>
  );
}
