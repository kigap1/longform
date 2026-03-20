"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { FilterBar } from "@/components/shared/filter-bar";
import { InstructionPanel } from "@/components/shared/instruction-panel";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { PageHeader } from "@/components/shared/page-header";
import { SectionCard } from "@/components/shared/section-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useIssuesQuery, useRankIssuesMutation } from "@/lib/api/hooks";
import { useProjectStore } from "@/lib/stores/project-store";


export default function IssuesPage() {
  const relatedArticlesRef = useRef<HTMLDivElement | null>(null);
  const projectId = useProjectStore((state) => state.currentProjectId);
  const stageInstruction = useProjectStore((state) => state.stageInstructions.issues ?? "");
  const selectedIssueId = useProjectStore((state) => state.selectedIssueId);
  const selectIssue = useProjectStore((state) => state.selectIssue);
  const { data, isLoading } = useIssuesQuery(projectId);
  const rankIssues = useRankIssuesMutation(projectId);
  const [activeFilter, setActiveFilter] = useState("전체");
  const [activeRegion, setActiveRegion] = useState("전체");
  const [sortOption, setSortOption] = useState("우선순위");
  const [keywordText, setKeywordText] = useState("");
  const [articleCountryFilter, setArticleCountryFilter] = useState("전체");

  const keywords = keywordText
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);

  const filteredItems = useMemo(() => {
    if (!data) return [];
    const byCategory =
      activeFilter === "전체" ? data.items : data.items.filter((item) => item.category === activeFilter);
    const byRegion =
      activeRegion === "전체" ? byCategory : byCategory.filter((item) => item.regions.includes(activeRegion));

    return [...byRegion].sort((left, right) => {
      if (sortOption === "기사 수") return right.articleCount - left.articleCount;
      if (sortOption === "인기순") {
        const leftPopularity = left.articles.reduce((sum, article) => sum + article.popularity, 0);
        const rightPopularity = right.articles.reduce((sum, article) => sum + article.popularity, 0);
        return rightPopularity - leftPopularity;
      }
      if (sortOption === "최신성") {
        const leftLatest = new Date(left.articles[0]?.publishedAt.replace(" ", "T") ?? 0).getTime();
        const rightLatest = new Date(right.articles[0]?.publishedAt.replace(" ", "T") ?? 0).getTime();
        return rightLatest - leftLatest;
      }
      return right.score - left.score;
    });
  }, [activeFilter, activeRegion, data, sortOption]);

  const selectedIssue =
    filteredItems.find((item) => item.id === selectedIssueId) ??
    data?.items.find((item) => item.id === selectedIssueId) ??
    filteredItems[0] ??
    data?.items[0] ??
    null;

  const selectedGroup = data?.groups.find((group) => group.issueId === selectedIssue?.id) ?? data?.groups[0] ?? null;
  const groupArticleFilters = useMemo(
    () => ["전체", ...new Set(selectedGroup?.articles.map((article) => article.country) ?? [])],
    [selectedGroup]
  );
  const visibleGroupArticles = useMemo(() => {
    if (!selectedGroup) return [];
    if (articleCountryFilter === "전체") return selectedGroup.articles;
    return selectedGroup.articles.filter((article) => article.country === articleCountryFilter);
  }, [articleCountryFilter, selectedGroup]);

  useEffect(() => {
    if (!selectedIssue && data?.items[0]) {
      selectIssue(data.items[0].id);
      return;
    }
    if (selectedIssue && selectedIssue.id !== selectedIssueId) {
      selectIssue(selectedIssue.id);
    }
  }, [data, selectIssue, selectedIssue, selectedIssueId]);

  useEffect(() => {
    if (!groupArticleFilters.includes(articleCountryFilter)) {
      setArticleCountryFilter("전체");
    }
  }, [articleCountryFilter, groupArticleFilters]);

  async function handleRankIssues() {
    await rankIssues.mutateAsync({
      project_id: projectId,
      keywords,
      user_instructions: stageInstruction
    });
  }

  function focusRelatedArticles(issueId: string, preferredCountry?: string) {
    selectIssue(issueId);
    if (preferredCountry) {
      setActiveRegion(preferredCountry);
      setArticleCountryFilter(preferredCountry);
    } else {
      setArticleCountryFilter("전체");
    }

    window.requestAnimationFrame(() => {
      relatedArticlesRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  if (isLoading || !data) {
    return <LoadingPanel label="이슈 탐색 화면을 준비하는 중입니다..." />;
  }

  return (
    <>
      <PageHeader
        eyebrow="1단계"
        title="이슈 탐색"
        description="한국·미국·글로벌 경제 뉴스를 프로젝트 맥락에 맞게 다시 모아, 유튜브 경제 채널에서 바로 활용할 만한 주제를 우선순위로 정리합니다."
        actions={[
          {
            label: rankIssues.isPending ? "기사 수집 중..." : "기사 수집 시작",
            variant: "primary",
            onClick: () => void handleRankIssues(),
            disabled: rankIssues.isPending
          },
          {
            label: rankIssues.isPending ? "랭킹 계산 중..." : "랭킹 다시 계산",
            variant: "secondary",
            onClick: () => void handleRankIssues(),
            disabled: rankIssues.isPending
          }
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
        <SectionCard title="뉴스 검색 키워드" description="쉼표로 나눠 입력하면 한국/미국/글로벌 기사 풀에서 관련 주제를 다시 조합합니다.">
          <div className="space-y-4">
            <Input
              value={keywordText}
              placeholder="예: 금리, 환율, FOMC, 한국 수출"
              onChange={(event) => setKeywordText(event.target.value)}
            />
            <div className="flex flex-wrap gap-2">
              {data.keywordSuggestions.map((keyword) => (
                <button
                  key={keyword}
                  type="button"
                  className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 transition hover:border-slate-300 hover:bg-slate-50"
                  onClick={() => {
                    setKeywordText((current) => {
                      const next = current
                        .split(",")
                        .map((value) => value.trim())
                        .filter(Boolean);
                      if (next.includes(keyword)) return current;
                      return [...next, keyword].join(", ");
                    });
                  }}
                >
                  {keyword}
                </button>
              ))}
            </div>
            <div className="flex justify-end">
              <Button onClick={() => void handleRankIssues()} disabled={rankIssues.isPending}>
                {rankIssues.isPending ? "반영 중..." : "키워드 반영"}
              </Button>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="수집 상태" description="현재 프로젝트에 연결된 기사 수집 상태와 발굴된 이슈 수를 보여줍니다.">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-sm text-slate-500">마지막 수집 시각</p>
              <p className="mt-2 text-lg font-semibold text-ink">{data.lastCollectedAt ?? "방금 전"}</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-sm text-slate-500">핵심 이슈 수</p>
              <p className="mt-2 text-lg font-semibold text-ink">{data.items.length}건</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-sm text-slate-500">가장 많이 붙은 기사</p>
              <p className="mt-2 text-lg font-semibold text-ink">
                {data.items.length ? Math.max(...data.items.map((item) => item.articleCount)) : 0}건
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-sm text-slate-500">포착 국가/권역</p>
              <p className="mt-2 text-lg font-semibold text-ink">{data.regionFilters.length - 1}개</p>
            </div>
          </div>
        </SectionCard>
      </div>

      {rankIssues.isError ? (
        <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {rankIssues.error instanceof Error ? rankIssues.error.message : "뉴스 랭킹 계산 중 오류가 발생했습니다."}
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        {data.highlights.map((highlight) => (
          <div
            key={highlight.issueId}
            className={`rounded-[24px] border p-5 transition ${
              highlight.tone === "hot"
                ? "border-emerald-200 bg-emerald-50"
                : highlight.tone === "watch"
                  ? "border-cyan-200 bg-cyan-50"
                  : "border-amber-200 bg-amber-50"
            }`}
          >
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
              {highlight.tone === "hot" ? "지금 뜨는 주제" : highlight.tone === "watch" ? "시장 연결 주제" : "콘텐츠 아이디어"}
            </p>
            <h3 className="mt-3 text-lg font-semibold text-ink">{highlight.title}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">{highlight.subtitle}</p>
            <Button className="mt-4" variant="ghost" onClick={() => focusRelatedArticles(highlight.issueId)}>
              이 이슈 보기
            </Button>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[1fr_1fr_0.8fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-4">
          <FilterBar title="이슈 분류" options={data.filters} value={activeFilter} onChange={setActiveFilter} />
        </div>
        <div className="rounded-[24px] border border-slate-200 bg-white p-4">
          <FilterBar title="국가 / 권역" options={data.regionFilters} value={activeRegion} onChange={setActiveRegion} />
        </div>
        <div className="rounded-[24px] border border-slate-200 bg-white p-4">
          <FilterBar title="정렬" options={data.sortOptions} value={sortOption} onChange={setSortOption} />
        </div>
      </div>

      <div className="panel-grid panel-grid-3 mt-6">
        <SectionCard title="랭킹 카드" description="이슈 우선순위, 기사 수, 국가 분포, 유튜브 확장 포인트를 한 번에 봅니다.">
          <div className="space-y-4">
            {filteredItems.map((issue) => (
              <div
                key={issue.id}
                className={`rounded-3xl border p-5 transition ${
                  selectedIssue?.id === issue.id ? "border-teal-400 bg-teal-50/40" : "border-slate-200 bg-slate-50/70"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex flex-wrap gap-2">
                      <Badge>{issue.category}</Badge>
                      {issue.regions.map((region) => (
                        <button
                          key={region}
                          type="button"
                          className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                            activeRegion === region
                              ? "border-cyan-300 bg-cyan-100 text-cyan-900"
                              : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                          }`}
                          onClick={() => {
                            setActiveRegion(region);
                            setArticleCountryFilter(region);
                            selectIssue(issue.id);
                          }}
                        >
                          {region}
                        </button>
                      ))}
                    </div>
                    <h3 className="mt-3 text-lg font-semibold text-ink">{issue.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{issue.summary}</p>
                  </div>
                  <Badge tone="success">우선 {issue.score.toFixed(2)}</Badge>
                </div>

                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200 bg-white p-3 text-sm text-slate-600">
                    <p className="font-medium text-ink">왜 지금 중요한가</p>
                    <p className="mt-2 leading-6">{issue.whyNow}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-3 text-sm text-slate-600">
                    <p className="font-medium text-ink">유튜브 주제 포인트</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {issue.youtubeAngles.map((angle) => (
                        <Badge key={angle}>{angle}</Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {issue.reasons.map((reason) => (
                    <Badge key={reason}>{reason}</Badge>
                  ))}
                  <Badge tone="warning">기사 {issue.articleCount}건</Badge>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Button variant="secondary" onClick={() => focusRelatedArticles(issue.id)}>
                    관련 기사 보기
                  </Button>
                  <Button variant={selectedIssue?.id === issue.id ? "primary" : "ghost"} onClick={() => selectIssue(issue.id)}>
                    프로젝트 이슈로 채택
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <div ref={relatedArticlesRef}>
          <SectionCard
            title={selectedIssue ? `관련 기사 그룹 · ${selectedIssue.title}` : "관련 기사 그룹"}
            description="가장 인기 있는 기사와 국가별 흐름을 같이 보면서, 실제 영상 주제 후보를 고를 수 있습니다."
          >
            {selectedIssue && selectedGroup ? (
              <div className="space-y-4">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex flex-wrap gap-2">
                  {selectedGroup.topSources.map((source) => (
                    <Badge key={source}>{source}</Badge>
                  ))}
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{selectedGroup.detail}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {groupArticleFilters.map((country) => (
                    <button
                      key={country}
                      type="button"
                      className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
                        articleCountryFilter === country
                          ? "border-navy bg-navy text-white"
                          : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                      }`}
                      onClick={() => setArticleCountryFilter(country)}
                    >
                      {country === "전체" ? "관련 기사 전체" : `${country} 기사만`}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                {visibleGroupArticles.map((article) => (
                  <div key={article.id} className="rounded-2xl border border-slate-200 p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge>{article.sourceName}</Badge>
                      <button
                        type="button"
                        className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                          articleCountryFilter === article.country
                            ? "border-cyan-300 bg-cyan-100 text-cyan-900"
                            : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                        }`}
                        onClick={() => setArticleCountryFilter(article.country)}
                      >
                        {article.country}
                      </button>
                      <Badge tone="warning">인기 {article.popularity}</Badge>
                    </div>
                    <h3 className="mt-3 font-semibold text-ink">{article.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{article.summary}</p>
                    <div className="mt-3 flex items-center justify-between gap-3 text-xs text-slate-500">
                      <span>{article.publishedAt}</span>
                      <a href={article.url} target="_blank" rel="noreferrer" className="font-medium text-teal-700 hover:text-teal-800">
                        기사 열기
                      </a>
                    </div>
                  </div>
                ))}
                {!visibleGroupArticles.length ? (
                  <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-sm text-slate-500">
                    현재 선택한 국가 조건에 맞는 관련 기사가 없습니다. 위 필터에서 다른 국가를 선택해 보세요.
                  </div>
                ) : null}
              </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-sm text-slate-500">
                선택된 이슈가 없습니다.
              </div>
            )}
          </SectionCard>
        </div>

        <div className="space-y-4">
          <InstructionPanel stageKey="issues" title="이슈 탐색 지시" />
          <SectionCard title="지시 반영 안내" description="오른쪽 지시문은 기사 수집과 랭킹 계산에 실제로 반영됩니다.">
            <div className="space-y-3 text-sm text-slate-600">
              <p className="rounded-2xl border border-slate-200 p-4">예: 한국 기사 비중을 높이고, 미국 거시경제 기사도 함께 포함</p>
              <p className="rounded-2xl border border-slate-200 p-4">예: 유튜브 영상 제목으로 쓰기 쉬운 갈등형 주제를 우선 정렬</p>
              <Button className="w-full" onClick={() => void handleRankIssues()} disabled={rankIssues.isPending}>
                {rankIssues.isPending ? "지시 반영 중..." : "지시 반영 후 다시 수집"}
              </Button>
            </div>
          </SectionCard>
        </div>
      </div>
    </>
  );
}
