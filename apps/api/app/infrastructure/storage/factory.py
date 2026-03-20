from __future__ import annotations

from app.core.config import get_settings
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.storage.s3 import S3CompatibleStorage
from app.infrastructure.storage.types import StoragePort


def build_storage() -> StoragePort:
    settings = get_settings()

    if settings.storage_mode == "s3":
        return S3CompatibleStorage(bucket_name=settings.s3_bucket_name)

    return LocalStorage(root=settings.local_storage_root)
