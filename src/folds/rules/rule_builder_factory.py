import re
from abc import ABC, abstractmethod
from typing import Callable, Protocol, cast

from telethon.events.common import EventBuilder

from folds.rules.parameter_types import RuleCallback
from folds.rules.rule import Rule


class RuleBuilderFactory(ABC):
    """
    Creates decorator factories. They can build rules and use them in the specified way.
    """

    @abstractmethod
    def _use_rule(self, rule: Rule): ...

    def create_rule_builder(self, event: EventBuilder) -> 'RuleBuilderProtocol':
        class NewRuleDecorator(RuleDecorator):
            _event = event
            _use_rule = self._use_rule

        return cast(RuleBuilderProtocol, NewRuleDecorator)

    def on(self, event: EventBuilder) -> Callable[[RuleCallback], RuleCallback]:
        return self.create_rule_builder(event)()


class RuleDecorator(ABC):
    """
    An object that decorates a handler function to create a rule.
    """

    _event: EventBuilder = NotImplemented
    _use_rule: Callable[[Rule], None] = NotImplemented

    def __init__(self, *, regex: str | re.Pattern | None = None):
        self.regex = re.compile(regex) if isinstance(regex, str) else regex

    def __call__(self, function: RuleCallback) -> RuleCallback:
        rule = Rule.from_function(self._event, function)
        if self.regex is not None:
            rule = rule.with_extra_condition(lambda event: bool(re.search(self.regex, event.raw_text)))

        self._use_rule(rule)
        return function


class RuleBuilderProtocol(Protocol):
    def __call__(self, *, regex: str | re.Pattern | None = None) -> RuleDecorator: ...
