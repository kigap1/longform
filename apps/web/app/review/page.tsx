"use client";

import { EvidencePanel } from "@/components/shared/evidence-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";
import { useReviewQuery } from "@/lib/api/hooks";


export default function ReviewPage() {
  const { data, isLoading } = useReviewQuery();

  if (isLoading || !data) {
    return <LoadingPanel label="검수 작업 공간을 준비하는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="9단계"
        title="검수 / 편집"
        description="대본, 근거 매핑, 장면 순서, 이미지 프롬프트를 버전 단위로 비교하고 복원할 수 있습니다."
        actions={[{ label: "새 버전 저장", variant: "primary" }, { label: "이전 버전 복원", variant: "secondary" }]}
      />

      <div className="panel-grid panel-grid-3">
        <SectionCard title="섹션 비교" description="수정 전후 내용을 나란히 보고 버전 차이를 검토합니다.">
          <div className="space-y-4">
            {data.sections.map((section) => (
              <div key={section.heading} className="grid gap-4 rounded-3xl border border-slate-200 p-5 xl:grid-cols-2">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-500">이전 버전</p>
                  <p className="mt-3 text-sm leading-7 text-slate-700">{section.content}</p>
                </div>
                <div className="rounded-2xl bg-mist p-4">
                  <p className="text-sm font-semibold text-teal-700">현재 버전</p>
                  <p className="mt-3 text-sm leading-7 text-slate-700">{section.content} 발표 시차 설명 문장을 추가했습니다.</p>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="근거 누락 점검" description="섹션별 근거 연결 상태를 검수합니다.">
          <EvidencePanel items={data.evidences} />
        </SectionCard>

        <SectionCard title="편집 액션" description="빠른 검수를 위한 운영 버튼 모음입니다.">
          <div className="space-y-3">
            <Button className="w-full justify-center" variant="secondary">
              숫자 근거 누락 검사
            </Button>
            <Button className="w-full justify-center" variant="secondary">
              장면 순서 재정렬
            </Button>
            <Button className="w-full justify-center" variant="secondary">
              이미지 프롬프트 동기화
            </Button>
          </div>
        </SectionCard>
      </div>
    </>
  );
}
