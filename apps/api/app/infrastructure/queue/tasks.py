from __future__ import annotations

from app.infrastructure.queue.celery_app import celery_app


@celery_app.task(name="jobs.issue_discovery")
def run_issue_discovery(project_id: str) -> dict[str, str]:
    return {"project_id": project_id, "status": "success", "message": "이슈 탐색 작업 완료"}


@celery_app.task(name="jobs.script_generation")
def run_script_generation(project_id: str, issue_id: str) -> dict[str, str]:
    return {
        "project_id": project_id,
        "issue_id": issue_id,
        "status": "success",
        "message": "대본 생성 작업 완료",
    }


@celery_app.task(name="jobs.image_generation")
def run_image_generation(project_id: str, scene_id: str) -> dict[str, str]:
    return {
        "project_id": project_id,
        "scene_id": scene_id,
        "status": "success",
        "message": "이미지 생성 작업 완료",
    }


@celery_app.task(name="jobs.video_preparation")
def run_video_preparation(project_id: str, scene_id: str) -> dict[str, str]:
    return {
        "project_id": project_id,
        "scene_id": scene_id,
        "status": "success",
        "message": "영상 번들 준비 완료",
    }


@celery_app.task(name="jobs.video_execution")
def run_video_execution(project_id: str, video_asset_id: str) -> dict[str, str]:
    return {
        "project_id": project_id,
        "video_asset_id": video_asset_id,
        "status": "success",
        "message": "mock 영상 실행 완료",
    }
