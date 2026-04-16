from pathlib import Path
from typing import Any

from folds.admin.admin import Admin, EmptyAdmin
from folds.app.app import App, _empty_context
from folds.app.bot_in_app import BotInApp
from folds.app.lifespan import default_lifespan, Lifespan
from folds.env_settings import settings


class Bot[T](BotInApp):
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
            context: T = _empty_context,  # ty: ignore[invalid-parameter-default]
            lifespan: Lifespan[App] = default_lifespan,
            default_session_directory: str | Path | None = None,
            admin: Admin = EmptyAdmin(),

            # Bot args:
            parse_mode: Any = None,
            **telethon_client_kwargs: Any,
    ):
        app = App[T](
            api_id=api_id,
            api_hash=api_hash,
            context=context,
            lifespan=lifespan,
            default_session_directory=default_session_directory,
            admin=admin,
        )
        super().__init__(
            token=token or settings.bot_token,
            app=app,
            parse_mode=parse_mode,
            **telethon_client_kwargs,
        )
        app.bots.append(self)

    def run(self):
        self.app.run()
