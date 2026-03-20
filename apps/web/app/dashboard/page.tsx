"use client";

import { useState } from "react";

import { EvidencePanel } from "@/components/shared/evidence-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { JobLogTable } from "@/components/shared/job-log-table";
import { MetricCard } from "@/components/shared/metric-card";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Tabs } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useDashboardQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function DashboardPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const { data, isLoading } = useDashboardQuery(projectId);
  const [activeTab, setActiveTab] = useState("오늘");

  if (isLoading || !data) {
    return <LoadingPanel label="대시보드 데이터를 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="운영 개요"
        title="콘텐츠 파이프라인 대시보드"
        description="이슈 우선순위, 근거 확보 상태, 생성 작업 진행 상황을 한 화면에서 확인합니다."
        actions={[{ label: "새 프로젝트", variant: "primary" }, { label: "근거 리포트 보기", variant: "secondary" }]}
      />

      <div className="mb-6">
        <Tabs items={data.tabs} value={activeTab} onChange={setActiveTab} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.metrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} change={metric.change} />
        ))}
      </div>

      <div className="panel-grid panel-grid-3 mt-6">
        <SectionCard title="우선순위 이슈" description="랭킹 사유가 바로 드러나도록 카드 형태로 정리했습니다.">
          <div className="space-y-4">
            {data.issues.map((issue) => (
              <div key={issue.id} className="rounded-3xl border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-slate-500">{issue.category}</p>
                    <h3 className="mt-1 font-semibold text-ink">{issue.title}</h3>
                  </div>
                  <Badge tone="success">점수 {issue.score.toFixed(2)}</Badge>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {issue.reasons.map((reason) => (
                    <Badge key={reason}>{reason}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="근거 맵 요약" description="공식 통계 우선 원칙과 보조 자료 경계를 동시에 표시합니다.">
          <EvidencePanel items={data.evidences} />
        </SectionCard>

        <SectionCard title="작업 현황" description="장기 실행 작업은 큐에서 추적하고 실패 시 재시도할 수 있습니다.">
          <JobLogTable items={data.jobs} />
        </SectionCard>
      </div>
    </>
  );
}
