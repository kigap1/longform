from unittest import TestCase

from app.domain.provider_interfaces import (
    CharacterProfilePayload,
    ImageSnapshotReferencePayload,
    InfographicStatCalloutPayload,
    KoreanInfographicLayoutPayload,
    SceneImageGenerationRequestPayload,
)
from app.domain.services.image_prompting import build_scene_image_prompt


class ImagePromptingTests(TestCase):
    def test_scene_image_prompt_builder_includes_character_layout_and_snapshots(self) -> None:
        prompt = build_scene_image_prompt(
            SceneImageGenerationRequestPayload(
                project_id="project-1",
                scene_id="scene-1",
                scene_title="환율 오프닝",
                scene_description="환율 상승 배경과 시청자 주의 포인트를 설명하는 장면",
                base_image_prompt="앵커가 환율 차트를 가리키는 장면",
                character_profile=CharacterProfilePayload(
                    character_profile_id="character-1",
                    name="한결 앵커",
                    description="신뢰감 있는 경제 앵커",
                    prompt_template="한국 경제 뉴스 앵커, 세로형 인포그래픽",
                    style_rules=["네이비 수트", "정면 구도"],
                    locked=True,
                ),
                project_locked_character=True,
                layout=KoreanInfographicLayoutPayload(
                    aspect_ratio="9:16",
                    layout_style="앵커+차트",
                    headline="원/달러 환율 점검",
                    subheadline="발표 숫자와 시장 반응을 함께 설명",
                    stat_callouts=[InfographicStatCalloutPayload(label="환율", value="1372.5", emphasis="high")],
                    caption_lines=["한국어 자막", "시장 반응은 보조자료"],
                    color_tokens=["navy", "red", "ivory"],
                ),
                reference_snapshots=[
                    ImageSnapshotReferencePayload(
                        snapshot_id="snapshot-1",
                        title="USD/KRW 캡처",
                        image_url="https://example.com/snapshot.png",
                        source_url="https://example.com/chart",
                        note="차트 레이아웃 참고",
                    )
                ],
                user_instructions="숫자를 크게 보여줘",
            )
        )

        self.assertIn("한결 앵커", prompt.prompt)
        self.assertIn("프로젝트 잠금 여부: 잠금", prompt.prompt)
        self.assertIn("원/달러 환율 점검", prompt.prompt)
        self.assertIn("환율 / 1372.5 / 강조 high", prompt.prompt)
        self.assertIn("USD/KRW 캡처", prompt.prompt)
        self.assertEqual(prompt.prompt_metadata["reference_snapshot_count"], 1)
