"use client";

import { cn } from "@/lib/utils";


type TabsProps = {
  items: readonly string[] | string[];
  value: string;
  onChange: (value: string) => void;
};

export function Tabs({ items, value, onChange }: TabsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <button
          key={item}
          type="button"
          onClick={() => onChange(item)}
          className={cn(
            "rounded-full border px-4 py-2 text-sm font-medium transition",
            value === item ? "border-navy bg-navy text-white" : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
          )}
        >
          {item}
        </button>
      ))}
    </div>
  );
}

