import json
from unittest import TestCase

from app.domain.provider_interfaces import SceneVideoPreparationRequestPayload, VerticalVideoInstructionsPayload
from app.domain.services.video_prompting import build_scene_video_prompt


class VideoPromptingTests(TestCase):
    def test_scene_video_prompt_builder_includes_vertical_video_instructions(self) -> None:
        result = build_scene_video_prompt(
            SceneVideoPreparationRequestPayload(
                project_id="project-1",
                scene_id="scene-1",
                scene_title="환율 오프닝",
                scene_description="환율 상승과 시장 반응을 설명하는 세로형 숏폼 장면",
                image_asset_id="image-1",
                image_asset_url="https://example.com/image.png",
                image_prompt="앵커와 환율 차트가 함께 보이는 장면",
                motion_prompt="차트 줌 인",
                bundle_path="/tmp/bundle.zip",
                download_path="/tmp/bundle.zip",
                vertical_instructions=VerticalVideoInstructionsPayload(
                    aspect_ratio="9:16",
                    duration_seconds=10,
                    framing="중앙 인물과 상단 제목 안전영역",
                    caption_style="굵은 한국어 자막",
                    pacing="fast",
                    motion_emphasis="high",
                ),
                user_instructions="숫자 자막을 크게 보여줘",
            )
        )

        self.assertIn("비율: 9:16", result.prompt)
        self.assertIn("길이: 10초", result.prompt)
        self.assertIn("숫자 자막을 크게 보여줘", result.prompt)
        self.assertIn("환율 오프닝", result.prompt)
        self.assertEqual(result.metadata["aspect_ratio"], "9:16")
        self.assertTrue(result.metadata["has_image_asset"])
