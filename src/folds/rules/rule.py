import inspect
from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from telethon.events.common import EventBuilder as EventBuilder, EventCommon

from folds.rules.parameter_types import parameter_types, RuleCallback
from folds.utils import await_if_needed
from folds.exceptions import FoldsRuleArgumentException

PreparedRuleCallback = Callable[[EventCommon], Awaitable[None]]


@dataclass(frozen=True)
class Rule:
    """
    An event handler.
    """

    event: EventBuilder
    callback: PreparedRuleCallback

    @classmethod
    def from_function(cls, event: EventBuilder, callback_function: RuleCallback):
        filter_function = event.func or (lambda x: True)

        signature = inspect.signature(callback_function)
        cls._validate_signature(signature, event)

        async def new_callback(update: EventCommon):
            check = filter_function(update)
            if not await await_if_needed(check):
                return

            values = {}
            for name, parameter in signature.parameters.items():
                for parameter_type in parameter_types:
                    if parameter_type.matches(parameter):
                        values[name] = await parameter_type.get_value(update)
                        break

            return_value = await callback_function(**values)
            if isinstance(return_value, str):
                await update.client.send_message(update.chat_id, return_value)

        event.func = None
        return Rule(event, new_callback)

    @classmethod
    def _validate_signature(cls, signature: inspect.Signature, event: EventBuilder):
        for name, parameter in signature.parameters.items():
            for parameter_type in parameter_types:
                if parameter_type.matches(parameter):
                    parameter_type.validate(parameter, event)
                    break
            else:
                raise FoldsRuleArgumentException(f"Argument '{name}' doesn't match any of Folds parameters.")

    def with_extra_condition(self, filter_function: Callable[[EventCommon], Any]) -> 'Rule':
        async def new_callback(update: EventCommon):
            check = filter_function(update)
            if not await await_if_needed(check):
                return

            return await self.callback(update)

        return Rule(self.event, new_callback)
