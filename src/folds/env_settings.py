import os
import re

from folds.exceptions import FoldsSetupException


class EnvSettings:
    @property
    def api_id(self) -> int:
        return _require_int_env('FOLDS_API_ID')

    @property
    def api_hash(self) -> str:
        return _require_env('FOLDS_API_HASH')

    @property
    def bot_token(self) -> str:
        return _require_env('FOLDS_BOT_TOKEN')

    @property
    def data_directory(self) -> str:
        default = '.folds'
        return os.environ.get('FOLDS_DATA_DIRECTORY', default)


settings = EnvSettings()


def _require_env(name: str, regexp: str | None = None) -> str:
    value = os.environ.get(name, None)
    if not value:
        raise FoldsSetupException(f'Please set environment variable {name} or specify the corresponding bot parameter.')
    if regexp and not re.fullmatch(regexp, value):
        raise FoldsSetupException(f'Environment variable {name} has invalid format.')
    return value


def _require_int_env(name: str) -> int:
    value = _require_env(name)
    if not value.isdigit():
        raise FoldsSetupException(f'Environment variable {name} must be a number.')
    return int(value)
