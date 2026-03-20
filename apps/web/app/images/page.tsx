"use client";

import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useImagesQuery } from "@/lib/api/hooks";


export default function ImagesPage() {
  const { data, isLoading } = useImagesQuery();

  if (isLoading || !data) {
    return <LoadingPanel label="이미지 장면 구성을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="7단계"
        title="이미지 생성"
        description="한국어 인포그래픽 스타일 장면 이미지를 생성하고, 장면별 프롬프트를 직접 수정하거나 재생성할 수 있습니다."
        actions={[{ label: "일괄 생성", variant: "primary" }, { label: "선택 장면 재생성", variant: "secondary" }]}
      />

      <div className="panel-grid panel-grid-3">
        <SectionCard title="장면별 프롬프트 편집" description="동일 캐릭터를 유지하면서도 장면 목적에 맞게 프롬프트를 조정합니다.">
          <div className="space-y-5">
            {data.scenes.map((scene) => (
              <div key={scene.title} className="rounded-3xl border border-slate-200 p-5">
                <div className="grid gap-5 lg:grid-cols-[180px_1fr]">
                  <div className="aspect-[3/4] rounded-[24px] bg-[linear-gradient(180deg,#112240,#0f766e)]" />
                  <div>
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold text-ink">{scene.title}</h3>
                        <p className="mt-1 text-sm text-slate-500">{scene.description}</p>
                      </div>
                      <Button variant="secondary">장면 재생성</Button>
                    </div>
                    <Textarea className="mt-4 min-h-28" defaultValue={scene.prompt} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="생성 기준" description="인포그래픽 가독성과 한국어 텍스트 레이아웃을 우선합니다.">
          <div className="space-y-3 text-sm leading-6 text-slate-600">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">필수 조건</p>
              <p className="mt-2">세로형 우선, 한국어 텍스트 포함, 숫자 강조 박스, 진행자 캐릭터 유지</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">참조 입력</p>
              <p className="mt-2">시장 스냅샷, 공식 통계 도표, 캐릭터 레퍼런스, 장면별 보조 이미지</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="images" title="이미지 생성 지시" />
      </div>
    </>
  );
}
