"use client";

import { useDeferredValue, useState, startTransition } from "react";

import Link from "next/link";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import { Bell, Search } from "lucide-react";

import { ProjectSelector } from "@/components/shared/project-selector";
import { useProjectsQuery, useWorkspaceSearchQuery } from "@/lib/api/hooks";
import { navigationItems } from "@/lib/navigation";
import { useProjectStore } from "@/lib/stores/project-store";
import { cn } from "@/lib/utils";


export function Topbar() {
  const currentProjectName = useProjectStore((state) => state.currentProjectName);
  const currentProjectId = useProjectStore((state) => state.currentProjectId);
  const { data: projects = [] } = useProjectsQuery();
  const pathname = usePathname();
  const router = useRouter();
  const currentProject = projects.find((project) => project.id === currentProjectId);
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const { data: searchResults = [] } = useWorkspaceSearchQuery(currentProjectId, deferredQuery);
  const shouldShowSearchResults = deferredQuery.trim().length >= 2 && searchResults.length > 0;

  return (
    <div className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/80 backdrop-blur">
      <header className="flex flex-wrap items-center justify-between gap-4 px-5 py-4">
        <div className="flex flex-wrap items-end gap-5">
          <ProjectSelector />
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-slate-500">현재 프로젝트</p>
            <h2 className="text-xl font-semibold text-ink">{currentProjectName}</h2>
            <p className="mt-1 text-sm text-slate-500">
              {currentProject?.stage ?? "대시보드"} · {currentProject?.updatedAt ?? "방금 전"} 업데이트
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative hidden sm:block">
            <label className="flex min-w-[300px] items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
              <Search className="h-4 w-4" />
              <input
                className="w-full bg-transparent outline-none"
                placeholder="이슈, 지표, 자산 검색"
                value={query}
                onChange={(event) => {
                  const nextValue = event.target.value;
                  startTransition(() => setQuery(nextValue));
                }}
              />
            </label>
            {shouldShowSearchResults ? (
              <div className="absolute right-0 top-[calc(100%+8px)] w-full rounded-3xl border border-slate-200 bg-white p-2 shadow-[0_18px_40px_rgba(15,23,42,0.08)]">
                {searchResults.map((result) => (
                  <button
                    key={result.id}
                    type="button"
                    className="flex w-full items-start justify-between gap-3 rounded-2xl px-3 py-3 text-left transition hover:bg-slate-50"
                    onClick={() => {
                      router.push(result.href as Route);
                      setQuery("");
                    }}
                  >
                    <div>
                      <p className="text-sm font-semibold text-ink">{result.title}</p>
                      <p className="mt-1 text-xs leading-5 text-slate-500">{result.detail}</p>
                    </div>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600">
                      {result.kind}
                    </span>
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <button className="rounded-2xl border border-slate-200 bg-white p-3 text-slate-600 transition hover:border-slate-300 hover:text-slate-900">
            <Bell className="h-4 w-4" />
          </button>
        </div>
      </header>

      <div className="flex gap-2 overflow-x-auto px-4 pb-4 lg:hidden">
        {navigationItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "whitespace-nowrap rounded-full border px-4 py-2 text-sm font-medium transition",
                active ? "border-navy bg-navy text-white" : "border-slate-200 bg-white text-slate-600"
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
