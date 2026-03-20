import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Button } from "@/components/ui/button";


const exports = [
  { title: "대본 내보내기", detail: "txt, md, docx-ready 구조", action: "대본 다운로드" },
  { title: "이미지 묶음", detail: "장면 이미지 zip", action: "이미지 zip 생성" },
  { title: "스냅샷 묶음", detail: "차트 캡처 zip", action: "스냅샷 zip 생성" },
  { title: "근거 리포트", detail: "json + 읽기용 markdown", action: "근거 리포트 다운로드" },
  { title: "프로젝트 번들", detail: "설정, 프롬프트, 산출물, 이력 일괄 내보내기", action: "프로젝트 번들 생성" }
] as const;

export default function DownloadsPage() {
  return (
    <>
      <PageHeader
        eyebrow="10단계"
        title="다운로드"
        description="스크립트, 이미지, 스냅샷, 근거 리포트, 프로젝트 번들을 다양한 포맷으로 내보낼 수 있습니다."
        actions={[{ label: "전체 번들 생성", variant: "primary" }]}
      />

      <div className="grid gap-4 xl:grid-cols-2">
        {exports.map((item) => (
          <SectionCard key={item.title} title={item.title} description={item.detail}>
            <Button variant="secondary">{item.action}</Button>
          </SectionCard>
        ))}
      </div>
    </>
  );
}

