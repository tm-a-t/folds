import os
from pathlib import Path

from telethon.sessions import Session

from folds.app.bot_client import BotClient
from folds.context import bot, client
from folds.rules.rule_builder_set import RuleBuilderSet
from folds.app.skill import Skill
from folds.rules.rule import Rule, PreparedRuleCallback

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from folds.app.app import App


class BotInApp(RuleBuilderSet):
    """
    Represents a bot as a part of an App. Provides methods for declaring bot rules.
    """

    def __init__(
            self,
            token: str,
            *,
            app: 'App',
            session: str | Path | Session | None = None,
            parse_mode: Any = None,
            **kwargs,
    ):
        super().__init__()
        self.bot_token = token
        self.app = app
        session = session or self._generate_session_filepath()
        self._client = BotClient(session, self.app.api_id, self.app.api_hash, **kwargs)
        self._client.parse_mode = parse_mode

    def _generate_session_filepath(self) -> str:
        self.app.default_session_directory.mkdir(exist_ok=True)
        filename = 'bot' + self.bot_token.split(':')[0]
        return self.app.default_session_directory / filename

    def use(self, *skill_list: Skill):
        for skill in skill_list:
            for rule in skill.rules:
                self._use_rule(rule)

    def _use_rule(self, rule: Rule):
        callback = self._transform_callback(rule.callback)
        self._client.add_event_handler(callback, rule.event)

    def _transform_callback(self, callback: PreparedRuleCallback) -> PreparedRuleCallback:
        async def new_function(event):
            with bot.using(self), client.using(self._client):
                await callback(event)

        return new_function

    async def authorize(self):
        await self._client.authorize(self.bot_token)

    async def run_in_app(self):
        await self._client.run_in_app()
