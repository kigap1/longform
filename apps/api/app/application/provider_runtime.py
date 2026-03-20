from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, cast

from app.core.config import Settings, get_settings
from app.infrastructure.db.repositories import RepositoryRegistry


AIProviderId = Literal["openai", "claude", "gemini", "kling"]
GenerationStage = Literal["script", "image", "video"]

AI_PROVIDER_ORDER: tuple[AIProviderId, ...] = ("openai", "claude", "gemini", "kling")

_PROVIDER_LABELS: dict[AIProviderId, str] = {
    "openai": "OpenAI",
    "claude": "Claude",
    "gemini": "Gemini",
    "kling": "Kling AI",
}

_PROVIDER_DESCRIPTIONS: dict[AIProviderId, str] = {
    "openai": "대본, 이미지, 비디오 준비 흐름을 단계적으로 연결할 수 있도록 준비된 OpenAI 경계입니다.",
    "claude": "근거 기반 대본 생성에 우선 연결된 Claude 경계입니다.",
    "gemini": "검색·생성 멀티모달 확장을 대비한 Gemini 경계입니다.",
    "kling": "비디오 단계용 Kling AI 경계입니다. 공식 웹앱에서 확인된 base URL을 기본값으로 넣고, 제출/상태조회 경로는 설정값으로 주입하도록 분리했습니다.",
}

_PROVIDER_FIELDS: dict[AIProviderId, tuple[dict[str, object], ...]] = {
    "openai": (
        {"key": "openai_api_key", "label": "OpenAI API 키", "placeholder": "비밀 키 입력", "secret": True},
        {"key": "openai_base_url", "label": "OpenAI Base URL", "placeholder": "https://api.openai.com/v1", "secret": False},
        {"key": "openai_model", "label": "OpenAI 텍스트 모델", "placeholder": "예: 설정할 모델", "secret": False},
        {"key": "openai_image_model", "label": "OpenAI 이미지 모델", "placeholder": "예: 설정할 이미지 모델", "secret": False},
        {"key": "openai_video_model", "label": "OpenAI 비디오 모델", "placeholder": "예: 설정할 비디오 모델", "secret": False},
    ),
    "claude": (
        {"key": "claude_api_key", "label": "Claude API 키", "placeholder": "비밀 키 입력", "secret": True},
        {"key": "claude_api_url", "label": "Claude API URL", "placeholder": "https://api.anthropic.com/v1/messages", "secret": False},
        {"key": "claude_api_version", "label": "Claude API 버전", "placeholder": "예: 2023-06-01", "secret": False},
        {"key": "claude_model", "label": "Claude 모델", "placeholder": "예: 설정할 모델", "secret": False},
    ),
    "gemini": (
        {"key": "gemini_api_key", "label": "Gemini API 키", "placeholder": "비밀 키 입력", "secret": True},
        {"key": "gemini_base_url", "label": "Gemini Base URL", "placeholder": "https://generativelanguage.googleapis.com", "secret": False},
        {"key": "gemini_model", "label": "Gemini 텍스트 모델", "placeholder": "예: 설정할 모델", "secret": False},
        {"key": "gemini_image_model", "label": "Gemini 이미지 모델", "placeholder": "예: 설정할 이미지 모델", "secret": False},
        {"key": "gemini_video_model", "label": "Gemini 비디오 모델", "placeholder": "예: 설정할 비디오 모델", "secret": False},
    ),
    "kling": (
        {"key": "kling_api_key", "label": "Kling API 키", "placeholder": "비밀 키 입력", "secret": True},
        {
            "key": "kling_base_url",
            "label": "Kling Base URL",
            "placeholder": "https://api-app-global.klingai.com",
            "secret": False,
        },
        {"key": "kling_video_model", "label": "Kling 비디오 모델", "placeholder": "예: kling-v1", "secret": False},
        {
            "key": "kling_submit_path",
            "label": "Kling submit 경로",
            "placeholder": "예: /api/video/submit 또는 브리지 URL",
            "secret": False,
        },
        {
            "key": "kling_status_path",
            "label": "Kling status 경로",
            "placeholder": "예: /api/video/status/{job_id}",
            "secret": False,
        },
        {
            "key": "kling_result_path",
            "label": "Kling result 경로",
            "placeholder": "예: /api/video/result/{job_id}",
            "secret": False,
        },
    ),
}

_DEFAULT_PROVIDER_KEYS: dict[GenerationStage, str] = {
    "script": "script_default_provider",
    "image": "image_default_provider",
    "video": "video_default_provider",
}

_DEFAULT_MODE_KEYS: dict[GenerationStage, str] = {
    "script": "script_provider_mode",
    "image": "image_provider_mode",
    "video": "video_provider_mode",
}

_STAGE_SUPPORT: dict[GenerationStage, dict[AIProviderId, dict[str, object]]] = {
    "script": {
        "openai": {
            "supported": True,
            "mock_available": True,
            "real_available": False,
            "note": "mock 테스트 가능, 실연동은 OpenAI 스크립트 adapter TODO 경계로 남겨둠",
        },
        "claude": {
            "supported": True,
            "mock_available": True,
            "real_available": True,
            "note": "mock 테스트 가능, 실제 Claude Messages API 연결 준비됨",
        },
        "gemini": {
            "supported": True,
            "mock_available": True,
            "real_available": False,
            "note": "mock 테스트 가능, 실연동은 Gemini 스크립트 adapter TODO 경계로 남겨둠",
        },
        "kling": {
            "supported": False,
            "mock_available": False,
            "real_available": False,
            "note": "Kling은 현재 대본 단계에서 사용하지 않습니다.",
        },
    },
    "image": {
        "openai": {
            "supported": True,
            "mock_available": True,
            "real_available": False,
            "note": "mock 테스트 가능, 실연동은 Nano Banana 스타일 매핑 TODO",
        },
        "claude": {
            "supported": False,
            "mock_available": False,
            "real_available": False,
            "note": "현재 이미지 생성 공급자로는 사용하지 않음",
        },
        "gemini": {
            "supported": True,
            "mock_available": True,
            "real_available": False,
            "note": "mock 테스트 가능, 실연동은 Gemini 이미지 adapter TODO",
        },
        "kling": {
            "supported": False,
            "mock_available": False,
            "real_available": False,
            "note": "Kling은 현재 이미지 단계에서 사용하지 않습니다.",
        },
    },
    "video": {
        "openai": {
            "supported": True,
            "mock_available": True,
            "real_available": False,
            "note": "mock 테스트 가능, 실연동은 OpenAI 비디오 workflow adapter TODO",
        },
        "claude": {
            "supported": False,
            "mock_available": False,
            "real_available": False,
            "note": "현재 비디오 준비 공급자로는 사용하지 않음",
        },
        "gemini": {
            "supported": True,
            "mock_available": True,
            "real_available": False,
            "note": "mock 테스트 가능, 실연동은 Gemini 비디오 workflow adapter TODO",
        },
        "kling": {
            "supported": True,
            "mock_available": True,
            "real_available": True,
            "note": "mock 테스트 가능. real 모드는 공식 웹앱에서 확인된 base URL을 기본값으로 쓰고, submit/status/result 경로는 설정값 또는 브리지로 주입합니다.",
        },
    },
}


def provider_label(provider_id: AIProviderId) -> str:
    return _PROVIDER_LABELS[provider_id]


def provider_description(provider_id: AIProviderId) -> str:
    return _PROVIDER_DESCRIPTIONS[provider_id]


def provider_fields(provider_id: AIProviderId) -> tuple[dict[str, object], ...]:
    return _PROVIDER_FIELDS[provider_id]


def stage_support(provider_id: AIProviderId, stage: GenerationStage) -> dict[str, object]:
    return _STAGE_SUPPORT[stage][provider_id]


def normalize_provider_id(value: str | None, default: AIProviderId = "openai") -> AIProviderId:
    normalized = (value or "").strip().lower()
    if normalized in AI_PROVIDER_ORDER:
        return cast(AIProviderId, normalized)
    return default


def normalize_provider_mode(value: str | None, default: str = "mock") -> str:
    normalized = (value or "").strip().lower()
    if normalized == "anthropic":
        return "real"
    if normalized in {"mock", "real"}:
        return normalized
    return default


@dataclass(slots=True)
class RuntimeSettingsResolver:
    repositories: RepositoryRegistry | None = None
    env_settings: Settings = field(default_factory=get_settings)
    _overrides: dict[str, str] | None = None

    def get(self, key: str, default: str | None = None) -> str | None:
        overrides = self._load_overrides()
        if key in overrides:
            return overrides[key]
        if hasattr(self.env_settings, key):
            value = getattr(self.env_settings, key)
            if value is None:
                return default
            if isinstance(value, bool):
                return "true" if value else "false"
            return str(value)
        return default

    def get_int(self, key: str, default: int) -> int:
        raw = self.get(key)
        if raw in {None, ""}:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    def default_provider(self, stage: GenerationStage) -> AIProviderId:
        default = normalize_provider_id(self.get(_DEFAULT_PROVIDER_KEYS[stage]), "openai")
        support = stage_support(default, stage)
        if support["supported"]:
            return default
        for provider_id in AI_PROVIDER_ORDER:
            if stage_support(provider_id, stage)["supported"]:
                return provider_id
        return "openai"

    def default_mode(self, stage: GenerationStage) -> str:
        env_default = "mock"
        if stage == "script":
            env_default = normalize_provider_mode(self.get("script_provider_mode"), "mock")
        elif stage == "image":
            env_default = normalize_provider_mode(self.get("image_provider_mode"), "mock")
        elif stage == "video":
            env_default = normalize_provider_mode(self.get("video_provider_mode"), "mock")
        return normalize_provider_mode(self.get(_DEFAULT_MODE_KEYS[stage]), env_default)

    def configured(self, key: str) -> bool:
        value = self.get(key)
        return value is not None and value.strip() != ""

    def _load_overrides(self) -> dict[str, str]:
        if self._overrides is None:
            self._overrides = {}
            if self.repositories is not None:
                for item in self.repositories.settings.list_all():
                    self._overrides[item.key] = item.value
        return self._overrides
