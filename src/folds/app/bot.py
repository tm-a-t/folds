from pathlib import Path
from typing import Any

from folds.admin.admin import Admin, EmptyAdmin
from folds.app import DEFAULT_DATA_DIRECTORY
from folds.app.app import App
from folds.app.bot_in_app import BotInApp
from folds.utils import require_env


class Bot(BotInApp):
    """
    A single-bot app.

    This derives from ``BotInApp`` to provide the methods for declaring bot's rules.
    """

    def __init__(
            self,
            token: str | None = None,
            api_id: int | None = None,
            api_hash: str | None = None,
            *,

            # App args:
            default_session_directory: str | Path = DEFAULT_DATA_DIRECTORY,
            admin: Admin = EmptyAdmin(),

            # Bot args:
            parse_mode: Any = None,
            **telethon_client_kwargs,
    ):
        app = App(
            api_id=api_id,
            api_hash=api_hash,
            default_session_directory=default_session_directory,
            admin=admin,
        )
        super().__init__(
            token=token or require_env('FOLDS_BOT_TOKEN'),
            app=app,
            parse_mode=parse_mode,
            **telethon_client_kwargs,
        )
        app.bots.append(self)

    def run(self):
        self.app.run()
