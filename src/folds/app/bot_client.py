import logging
from typing import Any, cast

import telethon.utils
from telethon import TelegramClient
from telethon.tl import types as tl_types

from folds.exceptions import FoldsInternalException
from folds.markup import html, markdown

logger = logging.getLogger(__name__)


def _parse_parse_mode(mode: Any) -> Any:
    mode_map = {'md': markdown, 'markdown': markdown, 'htm': html, 'html': html}
    if isinstance(mode, str):
        return mode_map[mode.lower()]
    else:
        return telethon.utils.sanitize_parse_mode(mode)


class BotClient(TelegramClient):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.parse_mode = 'md'

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

    @property
    def parse_mode(self) -> Any:
        return self._parse_mode

    @parse_mode.setter
    def parse_mode(self, mode: Any):
        self._parse_mode = _parse_parse_mode(mode)

    async def _parse_message_text(self, message: str, parse_mode: Any) -> tuple[str, list[tl_types.TypeMessageEntity]]:
        if parse_mode != ():
            parse_mode = _parse_parse_mode(parse_mode)
        return await super()._parse_message_text(message, parse_mode)
