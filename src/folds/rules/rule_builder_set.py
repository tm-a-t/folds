from abc import ABC
from typing import Callable, Any

from telethon import events
from telethon.events.common import EventCommon
from telethon.tl.custom import Message
import telethon.tl.types as tl_types

from folds.context import bot, client
from folds.rules.rule import Rule
from folds.rules.rule_builder_factory import RuleBuilderFactory, RuleBuilderProtocol


class BasicRuleBuilderSet(RuleBuilderFactory, ABC):
    """
    An abstract class for objects that can create simple rule kinds (like ``@bot.group_message``.)
    """

    def __init__(self):
        # Here, we essentially create shortcuts: this allows, for example,
        # using `bot.group_message` instead of `client.on(events.NewMessage(...))`

        self.group_message: RuleBuilderProtocol = self.create_rule_builder(
            events.NewMessage(func=lambda event: event.is_group, incoming=True)
        )
        self.private_message: RuleBuilderProtocol = self.create_rule_builder(
            events.NewMessage(func=lambda event: event.is_private, incoming=True)
        )
        self.channel_message: RuleBuilderProtocol = self.create_rule_builder(
            events.NewMessage(func=lambda event: _from_true_channel(event), incoming=True)
        )

        self.group_commands = CommandRuleBuilderSet(self, lambda event: event.is_group)
        self.private_commands = CommandRuleBuilderSet(self, lambda event: event.is_private)

        self.added_to_group: RuleBuilderProtocol = self.create_rule_builder(events.ChatAction(func=_added_to_group))
        self.removed_from_group: RuleBuilderProtocol = self.create_rule_builder(events.ChatAction(func=_removed_from_group))
        self.group_became_supergroup: RuleBuilderProtocol = self.create_rule_builder(events.ChatAction(func=_group_became_supergroup))

        self.inline_query: RuleBuilderProtocol = self.create_rule_builder(events.InlineQuery())


class RuleBuilderSet(BasicRuleBuilderSet, ABC):
    def __init__(self):
        super().__init__()
        self.admin_commands: CommandRuleBuilderSet = CommandRuleBuilderSet(self, lambda event: bot.app.admin.is_authorized(event))
        self.admin: AdminRuleBuilderSet = AdminRuleBuilderSet(self._use_rule)


class AdminRuleBuilderSet(BasicRuleBuilderSet):
    def __init__(self, use_rule: Callable[[Rule], None]):
        self.use_rule = use_rule
        super().__init__()

    def _use_rule(self, rule: Rule):
        self.use_rule(rule.with_extra_condition(lambda event: bot.app.admin.is_authorized(event)))


class CommandRuleBuilderSet:
    def __init__(self, condition_set: BasicRuleBuilderSet, filter_function: Callable[[Message], Any]):
        self._condition_set = condition_set
        self._filter_function = filter_function

    def __getattr__(self, command: str):
        def filter_events(event: Message):
            return _is_command(event.raw_text, command) and self._filter_function(event)

        return self._condition_set.create_rule_builder(events.NewMessage(func=filter_events, incoming=True))


def _is_command(text: str | None, command: str) -> bool:
    if not text:
        return False
    first_word = text.split(maxsplit=1)[0].lower()
    bot_username = '@' + client.me.username.lower()
    return '/' + command == first_word.removesuffix(bot_username)


def _from_true_channel(event: EventCommon) -> bool:
    return event.is_channel and not event.is_group


def _added_to_group(event: events.ChatAction.Event) -> bool:
    return (
            event.is_group
            and event.user_added
            and event.user.is_self
            and hasattr(event.original_update, 'new_participant')
    )


def _removed_from_group(event: events.ChatAction.Event) -> bool:
    return (
            event.is_group
            and event.user_kicked
            and event.user.is_self
    )


def _group_became_supergroup(event: events.ChatAction.Event) -> bool:
    return (
            isinstance(event, tl_types.UpdateNewChannelMessage)
            and isinstance(event.message, tl_types.MessageService)
            and isinstance(
                event.message.action, tl_types.MessageActionChannelMigrateFrom
            )
    )

