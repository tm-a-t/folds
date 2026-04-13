import os
from pathlib import Path

from telethon.sessions import Session

from folds.app.bot_client import BotClient
from folds.context import bot
from folds.rules.rule_builder_set import RuleBuilderSet
from folds.app.skill import Skill
from folds.rules.rule import Rule, PreparedRuleCallback

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from folds.app.app import App


class BotInApp(BotClient, RuleBuilderSet):
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
        RuleBuilderSet.__init__(self)

        self.bot_token = token
        self.app = app

        session = session or self._generate_session_filepath()
        BotClient.__init__(self, session, self.app.api_id, self.app.api_hash, **kwargs)
        self.parse_mode = parse_mode

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
        self.add_event_handler(callback, rule.event)

    def _transform_callback(self, callback: PreparedRuleCallback) -> PreparedRuleCallback:
        async def new_function(event):
            with bot.using(self):
                await callback(event)

        return new_function

    async def authorize_self(self):
        await self.authorize(self.bot_token)
