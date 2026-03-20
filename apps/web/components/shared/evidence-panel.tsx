import { Badge } from "@/components/ui/badge";


type EvidenceItem = {
  title: string;
  detail: string;
  tone: "verified" | "supplementary";
};

export function EvidencePanel({ items }: { items: ReadonlyArray<EvidenceItem> }) {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between gap-3">
            <p className="font-medium text-ink">{item.title}</p>
            <Badge tone={item.tone === "verified" ? "success" : "supplementary"}>
              {item.tone === "verified" ? "검증됨" : "보조 자료"}
            </Badge>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-500">{item.detail}</p>
        </div>
      ))}
    </div>
  );
}
