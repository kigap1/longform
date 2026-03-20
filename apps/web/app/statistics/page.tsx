"use client";

import { useMemo, useState } from "react";

import { EvidencePanel } from "@/components/shared/evidence-panel";
import { FilterBar } from "@/components/shared/filter-bar";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LinePreview } from "@/components/shared/line-preview";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useStatisticsQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function StatisticsPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const { data, isLoading } = useStatisticsQuery(projectId);
  const [activeFilter, setActiveFilter] = useState("전체");

  const filteredRows = useMemo(() => {
    if (!data) return [];
    if (activeFilter === "전체") return data.items;
    if (activeFilter === "최신") return data.items.filter((row) => !row.stale);
    return data.items.filter((row) => row.stale);
  }, [data, activeFilter]);

  if (isLoading || !data) {
    return <LoadingPanel label="통계 검증 화면을 준비하는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="2단계"
        title="통계 검증"
        description="ECOS, KOSIS, FRED, OECD 같은 공식 통계를 우선 추천하고, 수치 근거의 최신성까지 점검합니다."
        actions={[{ label: "지표 추천", variant: "primary" }, { label: "팩트 체크 실행", variant: "secondary" }]}
      />

      <div className="mb-6">
        <FilterBar title="데이터 상태 필터" options={data.filters} value={activeFilter} onChange={setActiveFilter} />
      </div>

      <div className="panel-grid panel-grid-3">
        <SectionCard title="추천 지표" description="이슈와 연결된 지표를 검토하고 근거로 채택할 수 있습니다.">
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeader>지표</TableHeader>
                  <TableHeader>최신값</TableHeader>
                  <TableHeader>이전값</TableHeader>
                  <TableHeader>발표일</TableHeader>
                  <TableHeader>상태</TableHeader>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredRows.map((row) => (
                  <TableRow key={row.code}>
                    <TableCell>
                      <p className="font-medium text-ink">{row.name}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {row.source} · {row.code}
                      </p>
                    </TableCell>
                    <TableCell>{row.latest}</TableCell>
                    <TableCell>{row.previous}</TableCell>
                    <TableCell>{row.releaseDate}</TableCell>
                    <TableCell>
                      <Badge tone={row.stale ? "warning" : "success"}>{row.stale ? "오래됨" : "최신"}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </SectionCard>

        <SectionCard title="시계열 미리보기" description="선택 지표의 흐름을 빠르게 확인하는 영역입니다.">
          <div className="space-y-4">
            {filteredRows.map((row) => (
              <div key={row.code} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-medium text-ink">{row.name}</p>
                    <p className="mt-1 text-sm text-slate-500">{row.releaseDate} 기준</p>
                  </div>
                  <Badge>{row.latest}</Badge>
                </div>
                <div className="mt-4">
                  <LinePreview values={[...row.series]} />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <div className="space-y-6">
          <SectionCard title="근거 컨텍스트" description="대본 생성 전 모든 수치 주장에 연결될 근거 묶음입니다.">
            <EvidencePanel items={data.evidences.slice(0, 2)} />
          </SectionCard>
          <InstructionPanel stageKey="statistics" title="통계 검증 지시" />
        </div>
      </div>
    </>
  );
}
