from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.application.schemas.assets import (
    VideoAssetSummary,
    VideoExecutionRequest,
    VideoExecutionSummary,
    VideoPrepareRequest,
)
from app.presentation.api.errors import raise_service_http_error
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/prepare", response_model=list[VideoAssetSummary])
def prepare_videos(payload: VideoPrepareRequest, services: ServiceBundleDep) -> list[VideoAssetSummary]:
    try:
        return services.videos.prepare(payload)
    except Exception as exc:
        raise_service_http_error(exc)


@router.post("/execute", response_model=list[VideoExecutionSummary])
def execute_videos(payload: VideoExecutionRequest, services: ServiceBundleDep) -> list[VideoExecutionSummary]:
    try:
        return services.videos.execute(payload)
    except Exception as exc:
        raise_service_http_error(exc)


@router.get("/bundles/{video_asset_id}")
def download_video_bundle(
    video_asset_id: str,
    services: ServiceBundleDep,
    project_id: str = Query(...),
) -> FileResponse:
    try:
        bundle_path = services.videos.bundle_path(project_id, video_asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    path = Path(bundle_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Bundle file not found: {bundle_path}")
    return FileResponse(path, media_type="application/zip", filename=path.name)
