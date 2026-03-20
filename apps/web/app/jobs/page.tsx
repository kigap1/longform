"use client";

import { useMemo, useState } from "react";

import { FilterBar } from "@/components/shared/filter-bar";
import { JobStatusBoard } from "@/components/shared/job-status-board";
import { JobLogTable } from "@/components/shared/job-log-table";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { useJobsQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function JobsPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const { data, isLoading } = useJobsQuery(projectId);
  const [statusFilter, setStatusFilter] = useState("전체");

  const filteredItems = useMemo(() => {
    if (!data) return [];
    if (statusFilter === "전체") return data.items;
    return data.items.filter((item) => item.status === statusFilter);
  }, [data, statusFilter]);

  if (isLoading || !data) {
    return <LoadingPanel label="작업 로그를 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="비동기 작업"
        title="작업 로그"
        description="장기 실행 작업은 큐를 통해 처리하고, 상태와 로그를 실시간으로 추적합니다."
        actions={[{ label: "실패 작업 재시도", variant: "primary" }, { label: "로그 새로고침", variant: "secondary" }]}
      />

      <div className="space-y-6">
        <JobStatusBoard items={data.summary} />
        <FilterBar title="작업 상태 필터" options={data.statuses} value={statusFilter} onChange={setStatusFilter} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_0.9fr]">
        <SectionCard title="작업 상태" description="대기, 실행 중, 성공, 실패 상태를 모두 남깁니다.">
          <JobLogTable items={filteredItems} />
        </SectionCard>

        <SectionCard title="운영 액션" description="재시도와 오류 복구를 위한 빠른 액션 버튼입니다.">
          <div className="space-y-3">
            <Button className="w-full justify-center" variant="secondary">
              이슈 탐색 작업 재실행
            </Button>
            <Button className="w-full justify-center" variant="secondary">
              이미지 생성 작업 재시도
            </Button>
            <Button className="w-full justify-center" variant="secondary">
              영상 번들 작업 재시도
            </Button>
          </div>
        </SectionCard>
      </div>
    </>
  );
}
