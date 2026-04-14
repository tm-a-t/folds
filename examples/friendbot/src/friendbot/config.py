import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUESTION_FILE = PROJECT_ROOT / "questions.txt"
DEFAULT_GROUPS_DB = PROJECT_ROOT / "groups.sqlite"


@dataclass(frozen=True)
class Settings:
    question_file: Path
    groups_db_path: Path
    poll_hour: int
    poll_minute: int
    poll_timezone: str
    log_level: str
    admin_user_ids: set[int]


def load_settings() -> Settings:
    return Settings(
        question_file=_resolve_path("QUESTION_FILE", DEFAULT_QUESTION_FILE),
        groups_db_path=_resolve_path("GROUPS_DB_PATH", DEFAULT_GROUPS_DB),
        poll_hour=int(os.getenv("POLL_HOUR", "10")),
        poll_minute=int(os.getenv("POLL_MINUTE", "0")),
        poll_timezone=os.getenv("POLL_TIMEZONE", "UTC"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        admin_user_ids=_parse_admin_ids(),
    )


def _resolve_path(env_name: str, default: Path) -> Path:
    raw = os.getenv(env_name, "").strip()
    return Path(raw).expanduser() if raw else default


def _parse_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_USER_IDS", "").strip()
    if not raw:
        return set()

    admin_ids: set[int] = set()
    for token in raw.split(","):
        value = token.strip()
        if not value:
            continue

        if value.lstrip("-").isdigit():
            admin_ids.add(int(value))
            continue

        logger.warning("Ignoring non-numeric admin id value: %s", value)

    return admin_ids
