from enum import Enum

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python 3.10 compatibility for local tests
    class StrEnum(str, Enum):
        pass


class IssueCategory(StrEnum):
    ECONOMY = "economy"
    INVESTING = "investing"
    GEOPOLITICS = "geopolitics"


class SourceKind(StrEnum):
    ARTICLE = "article"
    STATISTIC = "statistic"
    MARKET_DATA = "market_data"
    SNAPSHOT = "snapshot"


class ScriptStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"


class JobType(StrEnum):
    ISSUE_DISCOVERY = "issue_discovery"
    STAT_SYNC = "stat_sync"
    SCRIPT_GENERATION = "script_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_PREPARATION = "video_preparation"
    SNAPSHOT_CAPTURE = "snapshot_capture"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class AssetStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class EvidenceStatus(StrEnum):
    VERIFIED = "verified"
    STALE = "stale"
    CONFLICT = "conflict"
    MISSING = "missing"
