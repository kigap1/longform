from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

from app.domain.provider_interfaces import (
    ClaudeMessagesProviderPort,
    ClaudeMessagesRequestPayload,
    ClaudeMessagesResponsePayload,
    ScriptEvidenceMappingPayload,
    ScriptGenerationPayload,
    ScriptGenerationRequestPayload,
    ScriptScenePayload,
    ScriptSectionPayload,
    SectionRegenerationRequestPayload,
)
from app.domain.services.script_prompting import parse_generation_json, parse_regenerated_section_json


def _json_headers(api_key: str, api_version: str) -> dict[str, str]:
    return {
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": api_version,
    }


@dataclass(slots=True)
class ClaudeMessagesMockAdapter(ClaudeMessagesProviderPort):
    provider_name: str = "Claude Messages API"
    mode: str = "mock"
    model_name: str = "claude-messages-mock"

    def create_message(self, payload: ClaudeMessagesRequestPayload) -> ClaudeMessagesResponsePayload:
        fake_result = {
            "title": payload.metadata.get("issue_title", "팩트 기반 경제 이슈 해설"),
            "summary": "공식 통계와 시장 맥락을 함께 풀어낸 한국어 해설 대본 초안입니다.",
            "outline": ["문제 제기", "핵심 지표 확인", "시장 해석", "정리"],
            "sections": [
                {
                    "heading": "도입",
                    "content": "오늘 다룰 이슈가 왜 중요한지 먼저 짚고, 숫자를 볼 때 무엇을 조심해야 하는지 소개합니다.",
                    "evidence_ids": payload.metadata.get("primary_evidence_ids", "").split(",")[:1] if payload.metadata.get("primary_evidence_ids") else [],
                    "narration_purpose": "시청자의 관심을 끌고 해설의 기준을 제시합니다.",
                },
                {
                    "heading": "핵심 통계",
                    "content": "검증된 공식 통계를 중심으로 이슈의 방향성과 발표 시차를 설명합니다.",
                    "evidence_ids": payload.metadata.get("primary_evidence_ids", "").split(",") if payload.metadata.get("primary_evidence_ids") else [],
                    "narration_purpose": "수치 근거를 명확히 제시합니다.",
                },
                {
                    "heading": "시장 맥락",
                    "content": "시장 데이터는 보조 자료로만 활용해 투자 심리와 가격 반응을 덧붙입니다.",
                    "evidence_ids": payload.metadata.get("market_evidence_ids", "").split(",") if payload.metadata.get("market_evidence_ids") else [],
                    "narration_purpose": "공식 통계 이후 시장 반응을 연결합니다.",
                },
                {
                    "heading": "결론",
                    "content": "결국 핵심은 숫자의 절대값보다 방향, 시차, 근거 수준을 함께 읽는 것이라고 정리합니다.",
                    "evidence_ids": payload.metadata.get("primary_evidence_ids", "").split(",")[:1] if payload.metadata.get("primary_evidence_ids") else [],
                    "narration_purpose": "핵심 메시지를 회수합니다.",
                },
            ],
            "scenes": [
                {
                    "title": "오프닝",
                    "description": "앵커가 오늘 이슈의 중요성을 소개합니다.",
                    "image_prompt": "한국어 경제 뉴스 오프닝, 스튜디오 앵커, 핵심 키워드 자막",
                    "motion_prompt": "카메라 천천히 줌 인, 제목 강조",
                    "evidence_ids": payload.metadata.get("primary_evidence_ids", "").split(",")[:1] if payload.metadata.get("primary_evidence_ids") else [],
                },
                {
                    "title": "공식 통계 그래프",
                    "description": "공식 통계 그래프와 숫자 비교를 시각화합니다.",
                    "image_prompt": "한국어 인포그래픽, 공식 통계 차트, 수치 강조",
                    "motion_prompt": "차트 패닝, 수치 하이라이트",
                    "evidence_ids": payload.metadata.get("primary_evidence_ids", "").split(",") if payload.metadata.get("primary_evidence_ids") else [],
                },
                {
                    "title": "시장 반응",
                    "description": "환율 또는 자산 가격 흐름을 보조 자료로 제시합니다.",
                    "image_prompt": "시장 차트, 환율 또는 자산 가격, 보조자료 표기",
                    "motion_prompt": "차트 슬라이드, 보조자료 라벨 강조",
                    "evidence_ids": payload.metadata.get("market_evidence_ids", "").split(",") if payload.metadata.get("market_evidence_ids") else [],
                },
            ],
            "evidence_mappings": [
                {
                    "section_heading": "핵심 통계",
                    "evidence_ids": payload.metadata.get("primary_evidence_ids", "").split(",") if payload.metadata.get("primary_evidence_ids") else [],
                    "rationale": "공식 통계 근거로 주요 수치를 지지합니다.",
                },
                {
                    "section_heading": "시장 맥락",
                    "evidence_ids": payload.metadata.get("market_evidence_ids", "").split(",") if payload.metadata.get("market_evidence_ids") else [],
                    "rationale": "시장 보조 자료로 반응을 설명합니다.",
                },
            ],
        }
        return ClaudeMessagesResponsePayload(
            model=self.model_name,
            raw_text=json.dumps(fake_result, ensure_ascii=False),
            stop_reason="end_turn",
            input_tokens=800,
            output_tokens=1200,
        )

    def generate_script(self, payload: ScriptGenerationRequestPayload) -> ScriptGenerationPayload:
        if payload.prompt is None:
            raise ValueError("Claude mock provider requires a built prompt payload.")
        response = self.create_message(payload.prompt)
        parsed = parse_generation_json(response.raw_text)
        parsed.provider_model = response.model
        parsed.stop_reason = response.stop_reason
        parsed.input_tokens = response.input_tokens
        parsed.output_tokens = response.output_tokens
        return parsed

    def regenerate_section(self, payload: SectionRegenerationRequestPayload) -> ScriptSectionPayload:
        if payload.prompt is None:
            raise ValueError("Claude mock provider requires a built prompt payload.")
        evidence_ids = [item.evidence_id for item in payload.verified_statistics[:2] + payload.market_context[:1]]
        response = ClaudeMessagesResponsePayload(
            model=self.model_name,
            raw_text=json.dumps(
                {
                    "heading": payload.target_section_heading,
                    "content": (
                        f"{payload.target_section_heading} 재생성 초안입니다. "
                        f"{payload.user_instructions or '기존 흐름을 유지하면서 숫자 설명을 더 선명하게 다듬었습니다.'}"
                    ),
                    "evidence_ids": evidence_ids,
                    "narration_purpose": "기존 문맥을 유지하면서 논리와 근거 연결을 강화합니다.",
                },
                ensure_ascii=False,
            ),
            stop_reason="end_turn",
            input_tokens=300,
            output_tokens=220,
        )
        return parse_regenerated_section_json(response.raw_text)


@dataclass(slots=True)
class ClaudeMessagesAPIAdapter(ClaudeMessagesProviderPort):
    api_key: str | None
    api_url: str
    api_version: str
    model_name: str
    max_timeout_seconds: float = 45.0
    provider_name: str = "Claude Messages API"
    mode: str = "real"

    def create_message(self, payload: ClaudeMessagesRequestPayload) -> ClaudeMessagesResponsePayload:
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY is required when SCRIPT_PROVIDER_MODE=anthropic.")
        body = {
            "model": payload.model,
            "system": payload.system_prompt,
            "messages": [{"role": "user", "content": payload.user_prompt}],
            "max_tokens": payload.max_tokens,
            "temperature": payload.temperature,
        }
        req = request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers=_json_headers(self.api_key, self.api_version),
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.max_timeout_seconds) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Claude Messages API error: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Claude Messages API network error: {exc.reason}") from exc

        raw_text = "\n".join(
            block.get("text", "") for block in parsed.get("content", []) if block.get("type") == "text"
        ).strip()
        usage = parsed.get("usage", {})
        return ClaudeMessagesResponsePayload(
            model=parsed.get("model", payload.model),
            raw_text=raw_text,
            stop_reason=parsed.get("stop_reason"),
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
        )

    def generate_script(self, payload: ScriptGenerationRequestPayload) -> ScriptGenerationPayload:
        if payload.prompt is None:
            raise ValueError("Claude real provider requires a built prompt payload.")
        response = self.create_message(payload.prompt)
        parsed = parse_generation_json(response.raw_text)
        parsed.provider_model = response.model
        parsed.stop_reason = response.stop_reason
        parsed.input_tokens = response.input_tokens
        parsed.output_tokens = response.output_tokens
        return parsed

    def regenerate_section(self, payload: SectionRegenerationRequestPayload) -> ScriptSectionPayload:
        if payload.prompt is None:
            raise ValueError("Claude real provider requires a built prompt payload.")
        response = self.create_message(payload.prompt)
        return parse_regenerated_section_json(response.raw_text)
