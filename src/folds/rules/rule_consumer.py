from abc import ABC, abstractmethod
from typing import Callable

from telethon.events.common import EventBuilder

from folds.rules.parameter_types import RuleCallback
from folds.rules.rule import Rule


class RuleConsumer(ABC):
    """
    An object with an ``.on`` method.
    This method decorates a function to create a rule and then utilize it in some way.
    """

    @abstractmethod
    def _use_rule(self, rule: Rule): ...

    def on(self, event: EventBuilder) -> Callable[[RuleCallback], RuleCallback]:
        def decorator(function: RuleCallback) -> RuleCallback:
            rule = Rule.from_function(event, function)
            self._use_rule(rule)
            return function

        return decorator
