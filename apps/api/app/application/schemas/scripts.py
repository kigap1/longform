from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.application.schemas.common import APIModel, EvidenceReference


class ScriptGenerationRequest(APIModel):
    project_id: str
    issue_id: str
    issue_summary: str = ""
    statistic_ids: list[str] = Field(default_factory=list)
    market_data_ids: list[str] = Field(default_factory=list)
    indicator_codes: list[str] = Field(default_factory=list)
    market_symbols: list[str] = Field(default_factory=list)
    user_instructions: str = ""
    style_preset: str = "설명형"
    audience_type: str = "대중"
    tone: str = "차분한 분석형"
    provider_id: Literal["openai", "claude", "gemini"] | None = None
    provider_mode: str | None = None
    model_override: str | None = None


class ScriptSectionSummary(APIModel):
    id: str
    heading: str
    content: str
    evidence_ids: list[str] = Field(default_factory=list)
    narration_purpose: str = ""


class SceneSummary(APIModel):
    id: str
    title: str
    description: str
    image_prompt: str
    motion_prompt: str
    evidence_ids: list[str] = Field(default_factory=list)


class ScriptEvidenceMappingSummary(APIModel):
    section_heading: str
    evidence_ids: list[str] = Field(default_factory=list)
    rationale: str = ""


class ScriptSummary(APIModel):
    id: str
    issue_id: str | None = None
    title: str
    summary: str = ""
    outline: list[str] = Field(default_factory=list)
    hook: str = ""
    body: str = ""
    conclusion: str = ""
    version_number: int = 1
    provider_id: str = ""
    provider_name: str = ""
    provider_mode: str = ""
    style_preset: str = ""
    tone: str = ""
    audience_type: str = ""
    sections: list[ScriptSectionSummary] = Field(default_factory=list)
    scenes: list[SceneSummary] = Field(default_factory=list)
    evidence_mappings: list[ScriptEvidenceMappingSummary] = Field(default_factory=list)
    evidences: list[EvidenceReference] = Field(default_factory=list)


class RegenerateSectionRequest(APIModel):
    project_id: str
    script_id: str
    section_id: str
    mode: str = "section"
    user_instructions: str = ""
    style_preset: str | None = None
    audience_type: str | None = None
    tone: str | None = None
    provider_id: Literal["openai", "claude", "gemini"] | None = None
    provider_mode: str | None = None
    model_override: str | None = None


class RegenerateSectionResponse(APIModel):
    script_id: str
    version_number: int
    section: ScriptSectionSummary
