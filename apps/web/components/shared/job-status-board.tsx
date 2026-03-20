import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";


type JobStatusBoardProps = {
  items: ReadonlyArray<{ label: string; value: string; tone: "default" | "success" | "warning" | "danger" }>;
};

export function JobStatusBoard({ items }: JobStatusBoardProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <Card key={item.label} className="bg-white/90">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">{item.label}</p>
              <p className="mt-3 text-3xl font-semibold text-ink">{item.value}</p>
            </div>
            <Badge tone={item.tone}>{item.label}</Badge>
          </div>
        </Card>
      ))}
    </div>
  );
}
