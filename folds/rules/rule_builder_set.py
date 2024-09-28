from abc import ABC
from typing import Callable, Any

from telethon import events
from telethon.events.common import EventCommon
from telethon.tl.custom import Message

from folds.context import bot, client
from folds.rules.rule import Rule
from folds.rules.rule_consumer import RuleConsumer


class BasicRuleBuilderSet(RuleConsumer, ABC):
    def __init__(self):
        self.group_message = self.on(events.NewMessage(func=lambda event: event.is_group, incoming=True))
        self.private_message = self.on(events.NewMessage(func=lambda event: event.is_private, incoming=True))
        self.channel_message = self.on(events.NewMessage(func=lambda event: from_true_channel(event), incoming=True))

        self.group_commands = CommandRuleBuilder(self, lambda event: event.is_group)
        self.private_commands = CommandRuleBuilder(self, lambda event: event.is_private)

        self.added_to_group = self.on(events.ChatAction(func=added_to_group))
        self.removed_from_group = ...
        self.group_became_supergroup = ...


class RuleBuilderSet(BasicRuleBuilderSet, ABC):
    def __init__(self):
        super().__init__()
        self.admin_commands = CommandRuleBuilder(self, lambda event: bot.app.admin.is_authorized(event))
        self.admin = AdminRuleBuilderSet(self._use_rule)


class AdminRuleBuilderSet(BasicRuleBuilderSet):
    def __init__(self, use_rule: Callable[[Rule], None]):
        self.use_rule = use_rule
        super().__init__()

    def _use_rule(self, rule: Rule):
        self.use_rule(rule.with_extra_condition(lambda event: bot.app.admin.is_authorized(event)))


class CommandRuleBuilder:
    def __init__(self, condition_set: BasicRuleBuilderSet, filter_function: Callable[[Message], Any]):
        self._condition_set = condition_set
        self._filter_function = filter_function

    def __getattr__(self, command: str):
        def filter_events(event: Message):
            return is_command(event.raw_text, command) and self._filter_function(event)

        return self._condition_set.on(events.NewMessage(func=filter_events, incoming=True))


def is_command(text: str | None, command: str) -> bool:
    if not text:
        return False
    first_word = text.split(maxsplit=1)[0].lower()
    bot_username = '@' + client.me.username.lower()
    return '/' + command == first_word.removesuffix(bot_username)


def from_true_channel(event: EventCommon) -> bool:
    return event.is_channel and not event.is_group


def added_to_group(event: events.ChatAction.Event) -> bool:
    return (
            event.is_group
            and event.user_added
            and event.user.is_self
            and hasattr(event.original_update, 'new_participant')
    )
