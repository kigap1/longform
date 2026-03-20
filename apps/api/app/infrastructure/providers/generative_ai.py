from __future__ import annotations

from dataclasses import dataclass

from app.application.provider_runtime import AIProviderId, RuntimeSettingsResolver, provider_label
from app.domain.provider_interfaces import (
    ImageGenerationPayload,
    ImageGenerationPort,
    SceneImageGenerationRequestPayload,
    SceneVideoPreparationRequestPayload,
    ScriptGenerationPayload,
    ScriptGenerationRequestPayload,
    ScriptModelPort,
    ScriptSectionPayload,
    SectionRegenerationRequestPayload,
    VideoExecutionPayload,
    VideoExecutionRequestPayload,
    VideoPreparationPayload,
    VideoWorkflowPort,
)
from app.infrastructure.providers.adapters import MockImageGeneratorAdapter, MockVeoWorkflowAdapter
from app.infrastructure.providers.claude_messages import ClaudeMessagesAPIAdapter, ClaudeMessagesMockAdapter
from app.infrastructure.providers.kling_video import KlingVideoBridgeAdapter


@dataclass(slots=True)
class UnsupportedScriptProviderAdapter(ScriptModelPort):
    provider_name: str
    mode: str
    boundary_note: str

    def generate_script(self, payload: ScriptGenerationRequestPayload) -> ScriptGenerationPayload:
        _ = payload
        raise NotImplementedError(self.boundary_note)

    def regenerate_section(self, payload: SectionRegenerationRequestPayload) -> ScriptSectionPayload:
        _ = payload
        raise NotImplementedError(self.boundary_note)


@dataclass(slots=True)
class UnsupportedImageProviderAdapter(ImageGenerationPort):
    provider_name: str
    mode: str
    boundary_note: str

    def generate_image(self, payload: SceneImageGenerationRequestPayload) -> ImageGenerationPayload:
        _ = payload
        raise NotImplementedError(self.boundary_note)

    def edit_image(self, payload: SceneImageGenerationRequestPayload) -> ImageGenerationPayload:
        _ = payload
        raise NotImplementedError(self.boundary_note)


@dataclass(slots=True)
class UnsupportedVideoProviderAdapter(VideoWorkflowPort):
    provider_name: str
    mode: str
    boundary_note: str

    def prepare_scene(self, payload: SceneVideoPreparationRequestPayload) -> VideoPreparationPayload:
        _ = payload
        raise NotImplementedError(self.boundary_note)

    def execute_bundle(self, payload: VideoExecutionRequestPayload) -> VideoExecutionPayload:
        _ = payload
        raise NotImplementedError(self.boundary_note)


def build_script_provider(
    provider_id: AIProviderId,
    mode: str,
    runtime: RuntimeSettingsResolver,
) -> ScriptModelPort:
    label = provider_label(provider_id)
    if provider_id == "kling":
        return UnsupportedScriptProviderAdapter(
            provider_name=label,
            mode=mode,
            boundary_note="Kling AI는 현재 대본 단계에서 지원하지 않습니다.",
        )
    if mode == "mock":
        return ClaudeMessagesMockAdapter(provider_name=label, mode="mock", model_name=f"{provider_id}-script-mock")
    if provider_id == "claude":
        return ClaudeMessagesAPIAdapter(
            api_key=runtime.get("claude_api_key"),
            api_url=runtime.get("claude_api_url", runtime.env_settings.claude_api_url) or runtime.env_settings.claude_api_url,
            api_version=runtime.get("claude_api_version", runtime.env_settings.claude_api_version)
            or runtime.env_settings.claude_api_version,
            model_name=runtime.get("claude_model") or "",
            provider_name=label,
            mode="real",
        )
    if provider_id == "openai":
        return UnsupportedScriptProviderAdapter(
            provider_name=label,
            mode="real",
            boundary_note="TODO: OpenAI 스크립트 실연동 adapter를 확정한 뒤 real 모드를 활성화하세요. 지금은 mock 모드로 테스트할 수 있습니다.",
        )
    return UnsupportedScriptProviderAdapter(
        provider_name=label,
        mode="real",
        boundary_note="TODO: Gemini 스크립트 실연동 adapter를 확정한 뒤 real 모드를 활성화하세요. 지금은 mock 모드로 테스트할 수 있습니다.",
    )


def build_image_provider(
    provider_id: AIProviderId,
    mode: str,
    runtime: RuntimeSettingsResolver,
) -> ImageGenerationPort:
    _ = runtime
    label = provider_label(provider_id)
    if provider_id == "claude":
        return UnsupportedImageProviderAdapter(
            provider_name=label,
            mode=mode,
            boundary_note="Claude는 현재 이미지 생성 단계에서 지원하지 않습니다. OpenAI 또는 Gemini를 선택하세요.",
        )
    if provider_id == "kling":
        return UnsupportedImageProviderAdapter(
            provider_name=label,
            mode=mode,
            boundary_note="Kling AI는 현재 이미지 생성 단계에서 지원하지 않습니다. 비디오 단계에서만 선택하세요.",
        )
    if mode == "mock":
        return MockImageGeneratorAdapter(provider_name=label, mode="mock")
    return UnsupportedImageProviderAdapter(
        provider_name=label,
        mode="real",
        boundary_note=f"TODO: {label} 이미지 실연동 adapter 경계를 구체화한 뒤 real 모드를 활성화하세요. 지금은 mock 모드로 테스트할 수 있습니다.",
    )


def build_video_provider(
    provider_id: AIProviderId,
    mode: str,
    runtime: RuntimeSettingsResolver,
) -> VideoWorkflowPort:
    label = provider_label(provider_id)
    if provider_id == "claude":
        return UnsupportedVideoProviderAdapter(
            provider_name=label,
            mode=mode,
            boundary_note="Claude는 현재 비디오 준비/실행 단계에서 지원하지 않습니다. OpenAI 또는 Gemini를 선택하세요.",
        )
    if mode == "mock":
        return MockVeoWorkflowAdapter(provider_name=label, mode="mock")
    if provider_id == "kling":
        return KlingVideoBridgeAdapter(
            api_key=runtime.get("kling_api_key"),
            base_url=runtime.get("kling_base_url", runtime.env_settings.kling_base_url) or runtime.env_settings.kling_base_url,
            submit_path=runtime.get("kling_submit_path"),
            status_path=runtime.get("kling_status_path"),
            result_path=runtime.get("kling_result_path"),
            model_name=runtime.get("kling_video_model"),
            provider_name=label,
            mode="real",
        )
    return UnsupportedVideoProviderAdapter(
        provider_name=label,
        mode="real",
        boundary_note=f"TODO: {label} 비디오 workflow adapter 경계를 구체화한 뒤 real 모드를 활성화하세요. 지금은 mock 모드로 테스트할 수 있습니다.",
    )
