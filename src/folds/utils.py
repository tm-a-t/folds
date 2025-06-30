import inspect
import os
import re
from typing import Any

from folds.exceptions import FoldsSetupException


async def await_if_needed(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def require_env(name: str, regexp: str | None = None) -> str:
    value = os.environ.get(name, None)
    if not value:
        raise FoldsSetupException(f'Please set environment variable {name} or specify the corresponding bot parameter.')
    if regexp and not re.fullmatch(regexp, value):
        raise FoldsSetupException(f'Environment variable {name} has invalid format.')
    return value


def require_int_env(name: str) -> int:
    value = require_env(name)
    if not value.isdigit():
        raise FoldsSetupException(f'Environment variable {name} must be a number.')
    return int(value)
