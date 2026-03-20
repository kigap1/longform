"use client";

import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { useVideosQuery } from "@/lib/api/hooks";


export default function VideosPage() {
  const { data, isLoading } = useVideosQuery();

  if (isLoading || !data) {
    return <LoadingPanel label="영상 준비 장면을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="8단계"
        title="영상 생성"
        description="Veo 3.1 또는 동급 워크플로에 넘길 장면별 모션 지시, 프롬프트, 번들 구성을 준비합니다."
        actions={[{ label: "번들 준비", variant: "primary" }, { label: "세로형 설정 적용", variant: "secondary" }]}
      />

      <div className="panel-grid panel-grid-3">
        <SectionCard title="장면별 모션 설계" description="장면 순서, 카메라 움직임, 자막 타이밍을 함께 정의합니다.">
          <div className="space-y-4">
            {data.scenes.map((scene) => (
              <div key={scene.title} className="rounded-3xl border border-slate-200 p-5">
                <h3 className="text-lg font-semibold text-ink">{scene.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{scene.description}</p>
                <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">{scene.motion}</div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="번들 내보내기 규칙" description="프롬프트, 참조 이미지, 장면 메타데이터를 세트로 묶어 전달합니다.">
          <div className="space-y-3 text-sm leading-6 text-slate-600">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">포함 항목</p>
              <p className="mt-2">장면 프롬프트, 모션 지시, 참조 이미지, 캐릭터 잠금 규칙, 근거 요약</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">출력 방식</p>
              <p className="mt-2">장면별 JSON + 이미지 zip + 재생성용 텍스트 패키지</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="videos" title="영상 준비 지시" />
      </div>
    </>
  );
}
