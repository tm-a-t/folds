import asyncio
import logging
from contextlib import suppress
from pathlib import Path
from typing import Self

from telethon.helpers import get_running_loop
from telethon.sessions import Session

from folds.admin.admin import Admin, EmptyAdmin
from folds.app import DEFAULT_DATA_DIRECTORY
from folds.app.bot_in_app import BotInApp
from folds.app.lifespan import default_lifespan, Lifespan
from folds.utils import require_env

logger = logging.getLogger(__name__)


class App[T]:
    def __init__(
            self,
            api_id: int | None,
            api_hash: str | None,
            *,
            context: T = None,
            lifespan: Lifespan[Self] = default_lifespan,
            default_session_directory: str | Path = DEFAULT_DATA_DIRECTORY,
            admin: Admin = EmptyAdmin(),
            **common_bot_kwargs,
    ):
        self.api_id = api_id or require_env('FOLDS_API_ID')
        self.api_hash = api_hash or require_env('FOLDS_API_HASH')
        self.context = context
        self.lifespan = lifespan
        self.default_session_directory = Path(default_session_directory)
        self.admin = admin
        self.common_bot_kwargs = common_bot_kwargs

        self.bots: list[BotInApp] = []

    def create_bot(self, token: str, *, session: str | Path | Session | None = None, **kwargs) -> BotInApp:
        bot = BotInApp(
            token,
            app=self,
            session=session,
            **self.common_bot_kwargs,
            **kwargs,
        )
        self.bots.append(bot)
        return bot

    def run(self):
        loop = get_running_loop()
        task = loop.create_task(self._run())

        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            logger.info('Keyboard interrupt received. Shutting down...')
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)

    async def _run(self):
        coroutines = [bot.authorize_self() for bot in self.bots]
        await asyncio.gather(*coroutines)

        async with self.lifespan(self):
            logger.info('Folds app started')
            coroutines = [bot.run_in_app() for bot in self.bots]
            await asyncio.gather(*coroutines)
