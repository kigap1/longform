type LinePreviewProps = {
  values: number[];
  tone?: "accent" | "navy";
};

export function LinePreview({ values, tone = "accent" }: LinePreviewProps) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const points = values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * 100;
      const y = 100 - ((value - min) / Math.max(max - min, 1)) * 80 - 10;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox="0 0 100 100" className="h-20 w-full rounded-2xl bg-slate-50 p-2">
      <polyline
        fill="none"
        stroke={tone === "accent" ? "#0f766e" : "#112240"}
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}

