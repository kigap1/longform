"use client";

import { useMemo, useState } from "react";

import { FilterBar } from "@/components/shared/filter-bar";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LinePreview } from "@/components/shared/line-preview";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { useMarketQuery } from "@/lib/api/hooks";


export default function MarketPage() {
  const { data, isLoading } = useMarketQuery();
  const [period, setPeriod] = useState("오늘");

  const items = useMemo(() => data?.items ?? [], [data]);

  if (isLoading || !data) {
    return <LoadingPanel label="시장 데이터 화면을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="3단계"
        title="시장 데이터"
        description="주식, 금리, 원자재, 환율 등 보조 시장 데이터를 검색하고, 공식 통계와 구분해 프로젝트에 연결합니다."
        actions={[{ label: "자산 검색", variant: "primary" }, { label: "차트 연결", variant: "secondary" }]}
      />

      <div className="mb-6">
        <FilterBar title="조회 기간" options={data.periods} value={period} onChange={setPeriod} />
      </div>

      <div className="panel-grid panel-grid-3">
        <SectionCard title="자산 검색 결과" description="보조 자료로 사용할 자산을 자산군별로 정리합니다.">
          <div className="space-y-4">
            {items.map((item) => (
              <div key={item.symbol} className="rounded-3xl border border-slate-200 p-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-slate-500">{item.className}</p>
                    <h3 className="mt-1 font-semibold text-ink">{item.name}</h3>
                    <p className="mt-1 text-xs text-slate-500">
                      {item.source} · {item.symbol}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-semibold text-ink">{item.value}</p>
                    <Badge tone={item.change.startsWith("-") ? "danger" : "success"}>{item.change}</Badge>
                  </div>
                </div>
                <div className="mt-4">
                  <LinePreview values={[...item.series]} tone="navy" />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="사용 규칙" description="시장 포털 값은 보조 자료로 유지하고, 사실 주장에는 공식 값만 우선 사용합니다.">
          <div className="space-y-3 text-sm leading-6 text-slate-600">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="font-medium text-ink">공식 값 우선</p>
              <p className="mt-2">스크립트 숫자 문장은 공식 통계 근거가 연결되지 않으면 경고 상태로 남깁니다.</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="font-medium text-ink">보조 스냅샷 허용</p>
              <p className="mt-2">Yahoo Finance, Investing.com, Seeking Alpha 차트는 시각 자료 또는 맥락 설명용으로 저장합니다.</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="market" title="시장 데이터 지시" />
      </div>
    </>
  );
}
