from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.provider_interfaces import SceneVideoPreparationRequestPayload


@dataclass(slots=True)
class VideoPromptBuildResult:
    prompt: str
    motion_notes: str
    metadata: dict[str, object] = field(default_factory=dict)


def build_scene_video_prompt(payload: SceneVideoPreparationRequestPayload) -> VideoPromptBuildResult:
    vertical = payload.vertical_instructions
    sections = [
        "[장면 정보]",
        f"- 장면 제목: {payload.scene_title}",
        f"- 장면 설명: {payload.scene_description or '설명 없음'}",
        f"- 기준 이미지 프롬프트: {payload.image_prompt or '없음'}",
        f"- 기준 이미지 에셋: {payload.image_asset_url or '없음'}",
        f"- 기존 모션 힌트: {payload.motion_prompt or '없음'}",
        "[세로형 영상 지시]",
        f"- 비율: {vertical.aspect_ratio}",
        f"- 길이: {vertical.duration_seconds}초",
        f"- 프레이밍: {vertical.framing}",
        f"- 자막 스타일: {vertical.caption_style}",
        f"- 템포: {vertical.pacing}",
        f"- 모션 강조도: {vertical.motion_emphasis}",
        "[추가 지시]",
        f"- {payload.user_instructions or '없음'}",
        "[출력 규칙]",
        "- 세로형 숏폼 영상 기준으로 구성한다.",
        "- 한국어 자막 안전영역을 확보한다.",
        "- 첫 1초 안에 핵심 숫자나 질문을 노출한다.",
        "- 이미지의 인물/차트 구도를 유지한 채 카메라 무빙과 텍스트 애니메이션을 설계한다.",
    ]
    motion_notes = (
        "세로형 9:16 기준, 인물 중심 미디엄 샷 유지, "
        "첫 1초 헤드라인 등장, 차트 수치 하이라이트, "
        f"{vertical.motion_emphasis} 강도의 줌/패닝, {vertical.caption_style}"
    )
    return VideoPromptBuildResult(
        prompt="\n".join(sections),
        motion_notes=motion_notes,
        metadata={
            "scene_title": payload.scene_title,
            "aspect_ratio": vertical.aspect_ratio,
            "duration_seconds": vertical.duration_seconds,
            "has_image_asset": bool(payload.image_asset_url),
        },
    )
