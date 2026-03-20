from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse

from app.application.schemas.market import SnapshotCaptureRequest, SnapshotListResponse, SnapshotSummary
from app.presentation.api.dependencies import ServiceBundleDep


router = APIRouter()


@router.post("/capture", response_model=SnapshotSummary)
def capture_snapshot(payload: SnapshotCaptureRequest, services: ServiceBundleDep) -> SnapshotSummary:
    return services.snapshots.capture(payload)


@router.get("/list", response_model=SnapshotListResponse)
def list_snapshots(services: ServiceBundleDep, project_id: str | None = Query(None)) -> SnapshotListResponse:
    return services.snapshots.list(project_id)


@router.get("/preview/{snapshot_id}")
def preview_snapshot(snapshot_id: str, services: ServiceBundleDep):
    target = services.snapshots.preview_target(snapshot_id)
    if target is None:
        raise HTTPException(status_code=404, detail="snapshot not found")
    if target.startswith(("http://", "https://")):
        return RedirectResponse(target)
    if target.startswith("s3://"):
        raise HTTPException(status_code=501, detail="S3 preview URL generation is not implemented yet")

    file_path = Path(target)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="snapshot file not found")
    return FileResponse(file_path)
