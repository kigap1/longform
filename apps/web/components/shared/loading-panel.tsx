export function LoadingPanel({ label = "불러오는 중..." }: { label?: string }) {
  return (
    <div className="rounded-[28px] border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-panel">
      {label}
    </div>
  );
}

