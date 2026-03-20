"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigationItems } from "@/lib/navigation";
import { cn } from "@/lib/utils";


export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 shrink-0 flex-col bg-navy px-5 py-6 text-slate-100 lg:flex">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-teal-200/80">콘텐츠 스튜디오</p>
        <h1 className="mt-3 text-2xl font-semibold leading-tight">팩트 기반 AI 콘텐츠 스튜디오</h1>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          뉴스 탐색부터 통계 검증, 이미지·영상 준비까지 한 프로젝트 안에서 관리합니다.
        </p>
      </div>

      <nav className="mt-6 space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                active ? "bg-white text-navy shadow-lg" : "text-slate-200 hover:bg-white/10 hover:text-white"
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-3xl border border-teal-400/20 bg-teal-400/10 p-5 text-sm text-teal-50">
        <p className="font-semibold">운영 메모</p>
        <p className="mt-2 leading-6 text-teal-50/90">
          공식 통계를 우선 사용하고, 시장 포털 값은 보조 자료로만 연결되도록 설계했습니다.
        </p>
      </div>
    </aside>
  );
}

