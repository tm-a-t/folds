import asyncio
import logging
from pathlib import Path

from telethon.helpers import get_running_loop
from telethon.sessions import Session

from folds import BotInApp
from folds.admin.admin import Admin, EmptyAdmin

logger = logging.getLogger(__name__)


class App[T]:
    def __init__(
            self,
            api_id: int,
            api_hash: str,
            *,
            default_session_directory: str | Path = 'data',
            admin: Admin = EmptyAdmin(),
            **common_bot_kwargs,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.default_session_directory = Path(default_session_directory)
        self.admin = admin
        self.common_bot_kwargs = common_bot_kwargs

        self.bots: list[BotInApp] = []

    def bot(self, token: str, *, session: str | Path | Session | None = None, **kwargs):
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
        get_running_loop().run_until_complete(self._run())

    async def _run(self):
        coroutines = [bot.authorize() for bot in self.bots]
        await asyncio.gather(*coroutines)

        logger.info('Folds app started')

        coroutines = [bot.run_in_app() for bot in self.bots]
        await asyncio.gather(*coroutines)

    async def _run_test(self, coro):
        coroutines = [bot.authorize() for bot in self.bots]
        await asyncio.gather(*coroutines)

        await coro
        logger.info('Folds app started')

        coroutines = [bot.run_in_app() for bot in self.bots]
        await asyncio.gather(*coroutines)

