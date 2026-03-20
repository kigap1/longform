"use client";

import Image from "next/image";
import { useEffect, useState, type FormEvent } from "react";

import { FilterBar } from "@/components/shared/filter-bar";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { resolveApiUrl } from "@/lib/api/client";
import { useCaptureSnapshotMutation, useSnapshotsQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


function captureModeLabel(mode: string) {
  if (mode === "stub") return "스텁 캡처";
  if (mode === "real") return "실캡처";
  return mode;
}


export default function SnapshotsPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const projectName = useProjectStore((state) => state.currentProjectName);
  const { data, isLoading } = useSnapshotsQuery(projectId);
  const captureSnapshot = useCaptureSnapshotMutation(projectId);
  const [period, setPeriod] = useState("오늘");
  const [selectedSnapshotId, setSelectedSnapshotId] = useState<string>("");
  const [form, setForm] = useState({
    source_url: "https://finance.yahoo.com/quote/KRW=X",
    source_title: "Yahoo Finance USD/KRW",
    note: "환율 급등 구간을 강조해서 저장",
    evidence_label: "환율 차트 캡처 근거"
  });

  useEffect(() => {
    if (!data?.items.length) {
      setSelectedSnapshotId("");
      return;
    }
    const stillExists = data.items.some((item) => item.id === selectedSnapshotId);
    if (!stillExists) {
      setSelectedSnapshotId(data.items[0].id);
    }
  }, [data, selectedSnapshotId]);

  if (isLoading || !data) {
    return <LoadingPanel label="캡처 라이브러리를 불러오는 중입니다..." />;
  }

  const selectedSnapshot = data.items.find((item) => item.id === selectedSnapshotId) ?? data.items[0] ?? null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!form.source_url.trim()) return;
    const created = await captureSnapshot.mutateAsync({
      project_id: projectId,
      source_url: form.source_url.trim(),
      source_title: form.source_title.trim() || undefined,
      note: form.note.trim() || undefined,
      evidence_label: form.evidence_label.trim() || undefined,
      attach_as_evidence: true
    });
    setSelectedSnapshotId(created.id);
  }

  return (
    <>
      <PageHeader
        eyebrow="4단계"
        title="차트 / 캡처"
        description="시장 포털 또는 레퍼런스 페이지에서 차트 화면을 저장하고, 프로젝트와 근거 체인에 연결합니다. 현재 UI는 stub 캡처를 먼저 사용하고 있습니다."
      />

      <div className="mb-6">
        <FilterBar title="조회 기간" options={data.periods} value={period} onChange={setPeriod} />
      </div>

      <div className="panel-grid panel-grid-3">
        <SectionCard title="캡처 요청" description={`${projectName} 프로젝트에 연결되는 저장 요청입니다.`}>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">출처 URL</p>
              <Input
                value={form.source_url}
                onChange={(event) => setForm((current) => ({ ...current, source_url: event.target.value }))}
                placeholder="https://example.com/chart"
                required
              />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">출처 제목</p>
              <Input
                value={form.source_title}
                onChange={(event) => setForm((current) => ({ ...current, source_title: event.target.value }))}
                placeholder="페이지 제목 또는 차트 이름"
              />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">근거 라벨</p>
              <Input
                value={form.evidence_label}
                onChange={(event) => setForm((current) => ({ ...current, evidence_label: event.target.value }))}
                placeholder="근거 패널에 보일 라벨"
              />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">메모</p>
              <Textarea
                value={form.note}
                onChange={(event) => setForm((current) => ({ ...current, note: event.target.value }))}
                placeholder="왜 이 장면을 저장하는지 메모를 남겨주세요."
                className="min-h-28"
              />
            </div>
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
              현재 단계에서는 실제 브라우저 스크린샷 대신 stub 이미지를 저장합니다. URL, 제목, 시각, 메모, 프로젝트 링크, 근거 연결 구조는 실제 연동과 동일하게 유지됩니다.
            </div>
            {captureSnapshot.isError ? (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                {captureSnapshot.error instanceof Error ? captureSnapshot.error.message : "캡처 요청 중 오류가 발생했습니다."}
              </div>
            ) : null}
            <Button type="submit" disabled={captureSnapshot.isPending} className="w-full">
              {captureSnapshot.isPending ? "캡처 저장 중..." : "캡처 저장"}
            </Button>
          </form>
        </SectionCard>

        <SectionCard title="캡처 목록" description="출처 URL, 캡처 시각, 노트, 연결된 근거가 함께 저장됩니다.">
          <div className="grid gap-4">
            {data.items.map((snapshot) => (
              <button
                key={snapshot.id}
                type="button"
                onClick={() => setSelectedSnapshotId(snapshot.id)}
                className={`overflow-hidden rounded-3xl border text-left transition ${
                  selectedSnapshot?.id === snapshot.id
                    ? "border-teal-500 shadow-[0_20px_40px_rgba(15,118,110,0.12)]"
                    : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="relative aspect-[16/10] overflow-hidden bg-[linear-gradient(135deg,#112240,#0f766e)]">
                  <Image
                    src={resolveApiUrl(snapshot.preview_url)}
                    alt={snapshot.title}
                    fill
                    unoptimized
                    sizes="(min-width: 1280px) 30vw, 100vw"
                    className="object-cover"
                  />
                </div>
                <div className="space-y-3 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge>{snapshot.source_title}</Badge>
                    <Badge tone={snapshot.capture_mode === "stub" ? "warning" : "success"}>
                      {captureModeLabel(snapshot.capture_mode)}
                    </Badge>
                    <Badge tone="supplementary">근거 {snapshot.attached_evidences.length}건</Badge>
                  </div>
                  <div>
                    <h3 className="font-semibold text-ink">{snapshot.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-500">{snapshot.note}</p>
                  </div>
                  <p className="text-xs text-slate-400">{snapshot.captured_at}</p>
                </div>
              </button>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="미리보기 / 근거 연결" description="선택한 캡처의 preview와 연결된 evidence를 함께 확인합니다.">
          {selectedSnapshot ? (
            <div className="space-y-5">
              <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 aspect-[16/10]">
                <Image
                  src={resolveApiUrl(selectedSnapshot.preview_url)}
                  alt={selectedSnapshot.title}
                  fill
                  unoptimized
                  sizes="(min-width: 1280px) 30vw, 100vw"
                  className="object-cover"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge>{selectedSnapshot.source_title}</Badge>
                <Badge tone={selectedSnapshot.capture_mode === "stub" ? "warning" : "success"}>
                  {captureModeLabel(selectedSnapshot.capture_mode)}
                </Badge>
                <Badge tone="supplementary">프로젝트 연결됨</Badge>
              </div>
              {selectedSnapshot.integration_boundary_note ? (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
                  {selectedSnapshot.integration_boundary_note}
                </div>
              ) : null}
              <div className="grid gap-3 text-sm text-slate-600">
                <div className="rounded-2xl border border-slate-200 p-4">
                  <p className="font-medium text-ink">출처 URL</p>
                  <p className="mt-2 break-all">{selectedSnapshot.source_url}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4">
                  <p className="font-medium text-ink">캡처 시각</p>
                  <p className="mt-2">{selectedSnapshot.captured_at}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4">
                  <p className="font-medium text-ink">연결 근거</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedSnapshot.attached_evidences.length ? (
                      selectedSnapshot.attached_evidences.map((evidence) => (
                        <Badge key={evidence.evidence_id} tone="supplementary">
                          {evidence.label}
                        </Badge>
                      ))
                    ) : (
                      <p className="text-sm text-slate-500">아직 연결된 근거가 없습니다.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-sm text-slate-500">
              선택된 캡처가 없습니다.
            </div>
          )}
        </SectionCard>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <SectionCard title="캡처 메타데이터" description="스크립트, 이미지, 영상 단계에서 다시 추적할 수 있도록 동일한 구조를 유지합니다.">
          <div className="space-y-4 text-sm text-slate-600">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">필수 저장 항목</p>
              <p className="mt-2">출처 URL, 페이지 제목, 캡처 시각, 작성 메모, 프로젝트 ID, 저장 위치, 연결 근거 ID</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">활용 범위</p>
              <p className="mt-2">근거 패널, 이미지 생성 참고 이미지, 영상 장면 번들, 소스 리포트 내보내기, 리뷰 단계 증빙</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">현재 통합 경계</p>
              <p className="mt-2">브라우저 자동 캡처는 provider adapter 경계까지만 열어두었고, 실제 캡처 엔진은 차기 단계에서 교체하도록 분리했습니다.</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="snapshots" title="캡처 단계 지시" />
      </div>
    </>
  );
}
