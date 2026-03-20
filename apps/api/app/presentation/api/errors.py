from __future__ import annotations

from fastapi import HTTPException


def raise_service_http_error(exc: Exception) -> None:
    if isinstance(exc, NotImplementedError):
        raise HTTPException(status_code=501, detail=str(exc) or "아직 구현되지 않은 provider 경계입니다.") from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise exc
