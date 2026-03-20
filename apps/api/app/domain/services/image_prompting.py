from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.provider_interfaces import (
    CharacterProfilePayload,
    KoreanInfographicLayoutPayload,
    SceneImageGenerationRequestPayload,
)


@dataclass(slots=True)
class ImagePromptBuildResult:
    prompt: str
    prompt_metadata: dict[str, object] = field(default_factory=dict)


def build_scene_image_prompt(payload: SceneImageGenerationRequestPayload) -> ImagePromptBuildResult:
    layout = payload.layout or KoreanInfographicLayoutPayload(
        headline=payload.scene_title,
        subheadline=payload.scene_description[:80],
        caption_lines=["한국어 경제 인포그래픽", "숫자와 자막은 한국어만 사용"],
        color_tokens=["navy", "crimson", "ivory"],
    )
    base_prompt = (payload.prompt_override or payload.base_image_prompt or payload.scene_description).strip()
    sections = [
        "[장면 정보]",
        f"- 장면 제목: {payload.scene_title}",
        f"- 장면 설명: {payload.scene_description or '설명 없음'}",
        f"- 기본 장면 프롬프트: {base_prompt or '별도 프롬프트 없음'}",
        "[캐릭터 일관성]",
        *_character_lines(payload.character_profile, payload.project_locked_character),
        "[한국어 인포그래픽 레이아웃]",
        *_layout_lines(layout),
        "[참조 스냅샷]",
        *_snapshot_lines(payload.reference_snapshots),
        "[추가 지시]",
        f"- {payload.user_instructions or '없음'}",
        "[출력 규칙]",
        "- 한국어 자막과 숫자 표기를 사용한다.",
        "- 앵커/캐릭터 얼굴과 헤어, 의상 톤을 일관되게 유지한다.",
        "- 차트, 하단 자막, 통계 박스가 함께 보이는 세로형 인포그래픽 장면을 우선한다.",
        "- 시장 스냅샷은 구도와 정보 배치 참고용으로만 사용한다.",
    ]
    return ImagePromptBuildResult(
        prompt="\n".join(sections),
        prompt_metadata={
            "scene_title": payload.scene_title,
            "character_profile_id": payload.character_profile.character_profile_id,
            "project_locked_character": payload.project_locked_character,
            "reference_snapshot_count": len(payload.reference_snapshots),
            "layout_style": layout.layout_style,
            "aspect_ratio": layout.aspect_ratio,
        },
    )


def _character_lines(character: CharacterProfilePayload, project_locked: bool) -> list[str]:
    lines = [
        f"- 캐릭터 이름: {character.name}",
        f"- 캐릭터 설명: {character.description or '설명 없음'}",
        f"- 프롬프트 템플릿: {character.prompt_template}",
    ]
    if character.style_rules:
        lines.append(f"- 스타일 규칙: {', '.join(character.style_rules)}")
    if character.reference_assets:
        lines.append(f"- 참조 에셋: {', '.join(character.reference_assets)}")
    lines.append(f"- 프로젝트 잠금 여부: {'잠금' if project_locked else '선택형'}")
    return lines


def _layout_lines(layout: KoreanInfographicLayoutPayload) -> list[str]:
    lines = [
        f"- 비율: {layout.aspect_ratio}",
        f"- 레이아웃 스타일: {layout.layout_style}",
        f"- 헤드라인: {layout.headline or '장면 제목 사용'}",
        f"- 서브헤드: {layout.subheadline or '없음'}",
    ]
    if layout.stat_callouts:
        lines.extend(
            f"- 통계 콜아웃: {item.label} / {item.value} / 강조 {item.emphasis}" for item in layout.stat_callouts
        )
    else:
        lines.append("- 통계 콜아웃: 없음")
    if layout.caption_lines:
        lines.append(f"- 캡션 라인: {' | '.join(layout.caption_lines)}")
    if layout.color_tokens:
        lines.append(f"- 색상 토큰: {', '.join(layout.color_tokens)}")
    return lines


def _snapshot_lines(reference_snapshots) -> list[str]:
    if not reference_snapshots:
        return ["- 참조 스냅샷 없음"]
    return [
        f"- {snapshot.snapshot_id} | {snapshot.title} | {snapshot.source_url} | 메모 {snapshot.note or '없음'}"
        for snapshot in reference_snapshots
    ]
