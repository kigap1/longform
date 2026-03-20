"use client";

import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { useCharactersQuery } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function CharacterPage() {
  const projectId = useProjectStore((state) => state.currentProjectId);
  const { data, isLoading } = useCharactersQuery(projectId);

  if (isLoading || !data) {
    return <LoadingPanel label="캐릭터 프리셋을 불러오는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="6단계"
        title="캐릭터 설정"
        description="프로젝트 단위로 진행자 캐릭터를 고정하고, 이미지 전 장면에서 일관된 프롬프트 규칙을 유지합니다."
        actions={[{ label: "캐릭터 잠금", variant: "primary" }, { label: "프리셋 저장", variant: "secondary" }]}
      />

      <div className="panel-grid panel-grid-3">
        <SectionCard title="캐릭터 후보" description="한 프로젝트에서 하나의 진행자 프롬프트를 기준으로 장면 일관성을 유지합니다.">
          <div className="grid gap-4 md:grid-cols-2">
            {data.items.map((character) => (
              <div key={character.name} className="rounded-3xl border border-slate-200 p-5">
                <div className="aspect-[4/5] rounded-[24px] bg-[linear-gradient(135deg,#112240,#304c7c)]" />
                <div className="mt-4 flex items-center justify-between gap-4">
                  <h3 className="text-lg font-semibold text-ink">{character.name}</h3>
                  <Badge tone={character.locked ? "success" : "default"}>
                    {character.locked ? "잠금됨" : "선택 가능"}
                  </Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-500">{character.description}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {character.rules.map((rule) => (
                    <Badge key={rule}>{rule}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="일관성 규칙" description="프롬프트에 항상 포함될 스타일 규칙과 참조 자산을 관리합니다.">
          <div className="space-y-3 text-sm leading-6 text-slate-600">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">고정 속성</p>
              <p className="mt-2">헤어스타일, 복장 팔레트, 얼굴 비율, 스튜디오 톤, 카메라 거리</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium text-ink">참조 자산</p>
              <p className="mt-2">썸네일, 프롬프트 스냅샷, 이전 성공 이미지, 금지 요소 목록</p>
            </div>
          </div>
        </SectionCard>

        <InstructionPanel stageKey="character" title="캐릭터 설정 지시" />
      </div>
    </>
  );
}
