from fastapi import APIRouter

from app.presentation.api.routers import (
    characters,
    evidence,
    images,
    issues,
    jobs,
    market,
    projects,
    scripts,
    settings,
    snapshots,
    stats,
    videos,
)


api_router = APIRouter()
api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(snapshots.router, prefix="/snapshot", tags=["snapshot"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

