from __future__ import annotations

import json
from dataclasses import dataclass
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from app.domain.provider_interfaces import (
    SceneVideoPreparationRequestPayload,
    VideoExecutionPayload,
    VideoExecutionRequestPayload,
    VideoPreparationPayload,
    VideoWorkflowPort,
)


def _resolve_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _is_retryable_submit_error(error: Exception) -> bool:
    if isinstance(error, (ConnectionResetError, ConnectionRefusedError, TimeoutError, OSError)):
        return True
    if isinstance(error, URLError):
        return isinstance(error.reason, (ConnectionResetError, ConnectionRefusedError, TimeoutError, OSError))
    return False


@dataclass(slots=True)
class KlingVideoBridgeAdapter(VideoWorkflowPort):
    api_key: str | None
    base_url: str
    submit_path: str | None
    status_path: str | None
    result_path: str | None
    model_name: str | None = None
    provider_name: str = "Kling AI"
    mode: str = "real"
    submit_retry_count: int = 2
    retry_delay_seconds: float = 0.1

    def prepare_scene(self, payload: SceneVideoPreparationRequestPayload) -> VideoPreparationPayload:
        prompt = (
            f"{payload.scene_title} Kling 준비 프롬프트\n"
            f"{payload.image_prompt}\n"
            f"모션: {payload.motion_prompt}\n"
            f"세로형 비율 {payload.vertical_instructions.aspect_ratio}, "
            f"길이 {payload.vertical_instructions.duration_seconds}초"
        )
        return VideoPreparationPayload(
            scene_id=payload.scene_id,
            prompt=prompt,
            motion_notes=payload.motion_prompt or "장면 모션 지시 없음",
            bundle_path=payload.bundle_path,
            download_path=payload.download_path,
            image_asset_id=payload.image_asset_id,
            provider_name=self.provider_name,
        )

    def execute_bundle(self, payload: VideoExecutionRequestPayload) -> VideoExecutionPayload:
        if not self.api_key:
            raise NotImplementedError("Kling API 키가 없습니다. AI 연결 메뉴에서 키를 저장한 뒤 real 모드를 사용하세요.")
        if not self.submit_path:
            raise NotImplementedError(
                "Kling submit 경로가 비어 있습니다. 현재는 공식 base URL만 확인됐고 제출/상태조회 계약은 공개 확인되지 않았습니다. "
                "AI 연결 메뉴에서 Kling submit 경로를 공식 경로 또는 사내 브리지 경로로 입력하세요."
            )

        request_body = {
            "provider": "kling",
            "model": self.model_name,
            "project_id": payload.project_id,
            "scene_id": payload.scene_id,
            "video_asset_id": payload.video_asset_id,
            "bundle_path": payload.bundle_path,
            "status_path": self.status_path,
            "result_path": self.result_path,
            "user_instructions": payload.user_instructions,
        }
        request = Request(
            _resolve_url(self.base_url, self.submit_path),
            data=json.dumps(request_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        raw = self._submit_request(request)

        try:
            parsed = json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Kling submit 응답을 JSON으로 해석하지 못했습니다.") from exc

        provider_job_id = str(parsed.get("job_id") or parsed.get("id") or "").strip()
        if not provider_job_id:
            raise ValueError("Kling submit 응답에 job_id가 없습니다. 브리지 또는 공식 응답 매핑을 확인하세요.")

        status = str(parsed.get("status") or "queued")
        output_path = str(parsed.get("output_path") or parsed.get("download_url") or payload.bundle_path)
        bundle_path = str(parsed.get("bundle_path") or payload.bundle_path)
        return VideoExecutionPayload(
            video_asset_id=payload.video_asset_id,
            scene_id=payload.scene_id,
            provider_job_id=provider_job_id,
            status=status,
            output_path=output_path,
            bundle_path=bundle_path,
            provider_name=self.provider_name,
        )

    def _submit_request(self, request: Request) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self.submit_retry_count + 1):
            try:
                with urlopen(request, timeout=30) as response:
                    return response.read().decode("utf-8")
            except HTTPError as exc:
                message = exc.read().decode("utf-8", errors="ignore")
                raise ValueError(f"Kling submit 요청이 실패했습니다. status={exc.code}, body={message}") from exc
            except (URLError, ConnectionResetError, ConnectionRefusedError, TimeoutError, OSError) as exc:
                last_error = exc
                if attempt >= self.submit_retry_count or not _is_retryable_submit_error(exc):
                    reason = exc.reason if isinstance(exc, URLError) else exc
                    raise ValueError(f"Kling submit 요청에 실패했습니다: {reason}") from exc
                time.sleep(self.retry_delay_seconds)

        raise ValueError(f"Kling submit 요청에 실패했습니다: {last_error}")
