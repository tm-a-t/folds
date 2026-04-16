import logging
from typing import cast

from telethon import TelegramClient
from telethon.tl import types as tl_types

from folds.exceptions import FoldsInternalException

logger = logging.getLogger(__name__)


class BotClient(TelegramClient):
    me: tl_types.User

    async def _authorize(self, bot_token: str):
        await self.connect()
        me = await self.sign_in(bot_token=bot_token)
        if not isinstance(me, tl_types.User):
            raise FoldsInternalException('Did not log in as a bot')
        self.me = me

    @property
    def username(self) -> str:
        """Username, remembered at startup"""
        return cast('str', self.me.username)  # bots without usernames are technically possible but hard to find

    async def run_in_app(self):
        await self._run_until_disconnected()
