from __future__ import annotations

import json
from dataclasses import dataclass, field

from app.domain.provider_interfaces import (
    ClaudeMessagesRequestPayload,
    ScriptEvidencePayload,
    ScriptEvidenceMappingPayload,
    ScriptGenerationPayload,
    ScriptScenePayload,
    ScriptSectionPayload,
)


@dataclass(slots=True)
class PromptBuildResult:
    system_prompt: str
    user_prompt: str
    prompt_metadata: dict[str, object] = field(default_factory=dict)


def _format_evidence_lines(items: list[ScriptEvidencePayload], prefix: str) -> list[str]:
    if not items:
        return [f"- {prefix} 없음"]
    lines = []
    for item in items:
        value_part = f", 값 {item.value}" if item.value is not None else ""
        release_part = f", 발표일 {item.release_date}" if item.release_date else ""
        note_part = f", 메모 {item.note}" if item.note else ""
        lines.append(
            f"- {item.evidence_id} | {item.label} | {item.source_name} | {item.source_kind}{value_part}{release_part}{note_part}"
        )
    return lines


def build_script_generation_prompt(
    *,
    issue_title: str,
    issue_summary: str,
    verified_statistics: list[ScriptEvidencePayload],
    market_context: list[ScriptEvidencePayload],
    user_instructions: str,
    style_preset: str,
    tone: str,
    audience: str,
) -> PromptBuildResult:
    system_prompt = (
        "당신은 한국어 경제/금융/지정학 콘텐츠 전문 스크립트 작성자다.\n"
        "반드시 제공된 근거 ID만 사용해 수치 주장을 연결하고, 시장 데이터는 보조 자료로만 취급한다.\n"
        "응답은 JSON만 반환하고 설명 문장이나 코드펜스를 추가하지 않는다.\n"
        "JSON 스키마:\n"
        "{"
        '"title": "string",'
        '"summary": "string",'
        '"outline": ["string"],'
        '"sections": [{"heading": "string", "content": "string", "evidence_ids": ["string"], "narration_purpose": "string"}],'
        '"scenes": [{"title": "string", "description": "string", "image_prompt": "string", "motion_prompt": "string", "evidence_ids": ["string"]}],'
        '"evidence_mappings": [{"section_heading": "string", "evidence_ids": ["string"], "rationale": "string"}]'
        "}"
    )
    user_prompt = "\n".join(
        [
            f"[이슈 제목]\n{issue_title}",
            f"[이슈 요약]\n{issue_summary or '별도 요약 없음'}",
            f"[스타일 프리셋]\n{style_preset}",
            f"[톤]\n{tone}",
            f"[대상 독자]\n{audience}",
            f"[사용자 추가 지시]\n{user_instructions or '없음'}",
            "[검증된 공식 통계]",
            *_format_evidence_lines(verified_statistics, "공식 통계"),
            "[보조 시장 맥락]",
            *_format_evidence_lines(market_context, "보조 시장 자료"),
            "[작성 지침]",
            "- 10분 분량 한국어 스크립트로 구성한다.",
            "- 첫 섹션은 훅, 마지막 섹션은 결론 성격을 가져야 한다.",
            "- 장면은 섹션 흐름과 대응되도록 3~6개로 분해한다.",
            "- 수치가 들어간 문장은 반드시 evidence_ids에 대응되는 근거를 포함한다.",
            "- 확인되지 않은 숫자는 쓰지 않는다.",
        ]
    )
    return PromptBuildResult(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        prompt_metadata={
            "issue_title": issue_title,
            "style_preset": style_preset,
            "tone": tone,
            "audience": audience,
            "verified_statistics_count": len(verified_statistics),
            "market_context_count": len(market_context),
        },
    )


def build_section_regeneration_prompt(
    *,
    script_title: str,
    target_section_heading: str,
    target_section_content: str,
    other_sections: list[ScriptSectionPayload],
    verified_statistics: list[ScriptEvidencePayload],
    market_context: list[ScriptEvidencePayload],
    user_instructions: str,
    style_preset: str,
    tone: str,
    audience: str,
) -> PromptBuildResult:
    system_prompt = (
        "당신은 기존 스크립트의 한 섹션만 안전하게 재작성하는 한국어 경제 스크립트 편집자다.\n"
        "반드시 제공된 근거 ID만 사용하고, 응답은 JSON만 반환한다.\n"
        'JSON 스키마: {"heading": "string", "content": "string", "evidence_ids": ["string"], "narration_purpose": "string"}'
    )
    other_section_lines = [
        f"- {section.heading}: {section.content}" for section in other_sections if section.heading != target_section_heading
    ] or ["- 다른 섹션 정보 없음"]
    user_prompt = "\n".join(
        [
            f"[스크립트 제목]\n{script_title}",
            f"[재생성 대상 섹션]\n{target_section_heading}",
            f"[현재 섹션 내용]\n{target_section_content}",
            "[다른 섹션 문맥]",
            *other_section_lines,
            f"[스타일 프리셋]\n{style_preset}",
            f"[톤]\n{tone}",
            f"[대상 독자]\n{audience}",
            f"[사용자 추가 지시]\n{user_instructions or '없음'}",
            "[검증된 공식 통계]",
            *_format_evidence_lines(verified_statistics, "공식 통계"),
            "[보조 시장 맥락]",
            *_format_evidence_lines(market_context, "보조 시장 자료"),
        ]
    )
    return PromptBuildResult(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        prompt_metadata={
            "script_title": script_title,
            "target_section_heading": target_section_heading,
            "style_preset": style_preset,
            "tone": tone,
            "audience": audience,
        },
    )


def build_claude_messages_request(
    *,
    model: str,
    build_result: PromptBuildResult,
    max_tokens: int,
    temperature: float,
    metadata: dict[str, str] | None = None,
) -> ClaudeMessagesRequestPayload:
    return ClaudeMessagesRequestPayload(
        model=model,
        system_prompt=build_result.system_prompt,
        user_prompt=build_result.user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        metadata=metadata or {},
    )


def parse_generation_json(text: str) -> ScriptGenerationPayload:
    payload = json.loads(_strip_json_fence(text))
    sections = [
        ScriptSectionPayload(
            heading=item["heading"],
            content=item["content"],
            evidence_ids=item.get("evidence_ids", []),
            narration_purpose=item.get("narration_purpose", ""),
        )
        for item in payload.get("sections", [])
    ]
    scenes = [
        ScriptScenePayload(
            title=item["title"],
            description=item["description"],
            image_prompt=item["image_prompt"],
            motion_prompt=item["motion_prompt"],
            evidence_ids=item.get("evidence_ids", []),
        )
        for item in payload.get("scenes", [])
    ]
    evidence_mappings = [
        ScriptEvidenceMappingPayload(
            section_heading=item["section_heading"],
            evidence_ids=item.get("evidence_ids", []),
            rationale=item.get("rationale", ""),
        )
        for item in payload.get("evidence_mappings", [])
    ]
    return ScriptGenerationPayload(
        title=payload["title"],
        summary=payload.get("summary", ""),
        outline=payload.get("outline", []),
        sections=sections,
        scenes=scenes,
        evidence_mappings=evidence_mappings,
        raw_response_text=text,
    )


def parse_regenerated_section_json(text: str) -> ScriptSectionPayload:
    payload = json.loads(_strip_json_fence(text))
    return ScriptSectionPayload(
        heading=payload["heading"],
        content=payload["content"],
        evidence_ids=payload.get("evidence_ids", []),
        narration_purpose=payload.get("narration_purpose", ""),
    )


def _strip_json_fence(text: str) -> str:
    normalized = text.strip()
    if normalized.startswith("```"):
        lines = normalized.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return normalized
