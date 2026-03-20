import { cn } from "@/lib/utils";


type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-2xl px-4 py-2.5 text-sm font-medium transition",
        variant === "primary" && "bg-navy text-white hover:bg-slate-800",
        variant === "secondary" && "bg-white text-ink border border-slate-200 hover:border-slate-300",
        variant === "ghost" && "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
        className
      )}
      {...props}
    />
  );
}

