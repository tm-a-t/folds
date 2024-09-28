from pathlib import Path

from telethon.sessions import Session

from folds.admin.admin import Admin, EmptyAdmin
from folds.app.app import App
from folds.app.bot_in_app import BotInApp


class Bot(BotInApp):
    """A single-bot app."""

    def __init__(
            self,
            token: str,
            api_id: int,
            api_hash: str,
            *,

            # App args:
            default_session_directory: str | Path = 'data',
            admin: Admin = EmptyAdmin(),

            # Bot args:
            **telethon_client_kwargs,
    ):
        app = App(
            api_id=api_id,
            api_hash=api_hash,
            default_session_directory=default_session_directory,
            admin=admin,
        )
        super().__init__(
            token=token,
            app=app,
            **telethon_client_kwargs,
        )
        app.bots.append(self)

    def run(self):
        self.app.run()
