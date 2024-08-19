import logging

from telethon import TelegramClient
from telethon.tl import types as tl_types

logger = logging.getLogger(__name__)


class BotClient(TelegramClient):
    me: tl_types.User | None

    async def authorize(self, bot_token: str):
        await self.connect()
        self.me = await self.sign_in(bot_token=bot_token)

    async def run_in_app(self):
        await self._run_until_disconnected()
