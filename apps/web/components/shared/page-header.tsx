import { Button } from "@/components/ui/button";


type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description: string;
  actions?: {
    label: string;
    variant?: "primary" | "secondary" | "ghost";
    onClick?: () => void;
    disabled?: boolean;
  }[];
};

export function PageHeader({ eyebrow, title, description, actions = [] }: PageHeaderProps) {
  return (
    <div className="mb-6 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">{eyebrow}</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">{title}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600">{description}</p>
      </div>

      {actions.length > 0 ? (
        <div className="flex flex-wrap items-center gap-3">
          {actions.map((action) => (
            <Button key={action.label} variant={action.variant} onClick={action.onClick} disabled={action.disabled}>
              {action.label}
            </Button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
