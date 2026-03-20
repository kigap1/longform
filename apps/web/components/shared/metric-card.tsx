import { Card } from "@/components/ui/card";


type MetricCardProps = {
  label: string;
  value: string;
  change: string;
};

export function MetricCard({ label, value, change }: MetricCardProps) {
  return (
    <Card className="bg-white/90">
      <p className="text-sm text-slate-500">{label}</p>
      <div className="mt-4 flex items-end justify-between gap-4">
        <span className="text-3xl font-semibold text-ink">{value}</span>
        <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold text-teal-700">{change}</span>
      </div>
    </Card>
  );
}

