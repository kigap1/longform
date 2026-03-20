import { cn } from "@/lib/utils";


export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-[28px] border border-white/70 bg-white p-5 shadow-panel sm:p-6", className)}
      {...props}
    />
  );
}

