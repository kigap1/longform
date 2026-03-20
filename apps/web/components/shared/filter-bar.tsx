"use client";

import { Tabs } from "@/components/ui/tabs";


type FilterBarProps = {
  title: string;
  options: readonly string[] | string[];
  value: string;
  onChange: (value: string) => void;
};

export function FilterBar({ title, options, value, onChange }: FilterBarProps) {
  return (
    <div className="rounded-[24px] border border-slate-200 bg-white p-4 shadow-panel">
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      <div className="mt-3">
        <Tabs items={options} value={value} onChange={onChange} />
      </div>
    </div>
  );
}

