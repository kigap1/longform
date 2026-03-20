from unittest import TestCase

from app.domain.provider_interfaces import ScriptEvidencePayload, ScriptGenerationRequestPayload, SectionRegenerationRequestPayload
from app.domain.services.script_prompting import (
    build_claude_messages_request,
    build_script_generation_prompt,
    build_section_regeneration_prompt,
)
from app.infrastructure.providers.claude_messages import ClaudeMessagesMockAdapter


class ScriptPromptingTests(TestCase):
    def test_generation_prompt_contains_required_context_blocks(self) -> None:
        verified_statistics = [
            ScriptEvidencePayload(
                evidence_id="stat-1",
                label="ECOS 기준금리",
                source_kind="statistic",
                source_name="ECOS",
                source_url="https://ecos.bok.or.kr",
                release_date="2026-03-01",
                value=3.25,
                note="공식 통계",
            )
        ]
        market_context = [
            ScriptEvidencePayload(
                evidence_id="market-1",
                label="USD/KRW",
                source_kind="market_data",
                source_name="Yahoo Finance",
                source_url="https://finance.yahoo.com",
                release_date="2026-03-20",
                value=1372.5,
                note="보조 자료",
            )
        ]
        prompt = build_script_generation_prompt(
            issue_title="미국 금리와 원화 변동성",
            issue_summary="금리 기대 변화가 원화와 위험자산에 미치는 영향을 설명합니다.",
            verified_statistics=verified_statistics,
            market_context=market_context,
            user_instructions="숫자 설명을 쉽게 해줘",
            style_preset="설명형",
            tone="차분한 분석형",
            audience="대중",
        )
        self.assertIn("[이슈 요약]", prompt.user_prompt)
        self.assertIn("stat-1", prompt.user_prompt)
        self.assertIn("market-1", prompt.user_prompt)
        self.assertIn("JSON 스키마", prompt.system_prompt)

    def test_mock_provider_returns_sections_scenes_and_evidence_mapping(self) -> None:
        build_result = build_script_generation_prompt(
            issue_title="미국 금리와 원화 변동성",
            issue_summary="금리, 환율, 자금 흐름의 연결을 설명합니다.",
            verified_statistics=[
                ScriptEvidencePayload(
                    evidence_id="stat-1",
                    label="ECOS 기준금리",
                    source_kind="statistic",
                    source_name="ECOS",
                    source_url="https://ecos.bok.or.kr",
                )
            ],
            market_context=[],
            user_instructions="없음",
            style_preset="설명형",
            tone="차분한 분석형",
            audience="대중",
        )
        prompt_request = build_claude_messages_request(
            model="claude-messages-mock",
            build_result=build_result,
            max_tokens=2000,
            temperature=0.2,
            metadata={"issue_title": "미국 금리와 원화 변동성", "primary_evidence_ids": "stat-1"},
        )
        provider = ClaudeMessagesMockAdapter()
        result = provider.generate_script(
            ScriptGenerationRequestPayload(
                issue_title="미국 금리와 원화 변동성",
                issue_summary="금리, 환율, 자금 흐름의 연결을 설명합니다.",
                verified_statistics=[],
                market_context=[],
                prompt=prompt_request,
            )
        )
        self.assertGreaterEqual(len(result.sections), 3)
        self.assertGreaterEqual(len(result.scenes), 2)
        self.assertGreaterEqual(len(result.evidence_mappings), 1)
        self.assertEqual(result.provider_model, "claude-messages-mock")

    def test_section_regeneration_prompt_and_mock_provider_work_together(self) -> None:
        build_result = build_section_regeneration_prompt(
            script_title="금리와 환율 해설",
            target_section_heading="핵심 통계",
            target_section_content="기존 통계 설명",
            other_sections=[],
            verified_statistics=[],
            market_context=[],
            user_instructions="통계를 더 쉽게 풀어줘",
            style_preset="설명형",
            tone="차분한 분석형",
            audience="대중",
        )
        prompt_request = build_claude_messages_request(
            model="claude-messages-mock",
            build_result=build_result,
            max_tokens=1200,
            temperature=0.2,
        )
        provider = ClaudeMessagesMockAdapter()
        result = provider.regenerate_section(
            SectionRegenerationRequestPayload(
                script_title="금리와 환율 해설",
                target_section_id="section-1",
                target_section_heading="핵심 통계",
                target_section_content="기존 통계 설명",
                prompt=prompt_request,
                user_instructions="통계를 더 쉽게 풀어줘",
            )
        )
        self.assertEqual(result.heading, "핵심 통계")
        self.assertIn("재생성", result.content)
