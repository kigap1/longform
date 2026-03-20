from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services import ServiceBundle, build_service_bundle
from app.core.database import get_db_session


DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_service_bundle(session: DatabaseSession) -> ServiceBundle:
    return build_service_bundle(session)


ServiceBundleDep = Annotated[ServiceBundle, Depends(get_service_bundle)]
