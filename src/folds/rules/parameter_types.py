import inspect
from abc import ABC, abstractmethod
from typing import Annotated, Callable, Awaitable

import telethon.tl.types as tl_types
from telethon import events
from telethon.events.common import EventBuilder as EventBuilder, EventCommon
from telethon.tl.custom import Message
from telethon.tl.custom.chatgetter import ChatGetter

from folds.exceptions import FoldsRuleArgumentException

type ThisReplyTo = Annotated[Message | None, 'message to which the user replies']
type ThisChat = tl_types.Chat | tl_types.Channel | tl_types.User
type ThisSender = tl_types.User | tl_types.Channel
type ThisInputChat = tl_types.InputPeerChat | tl_types.InputPeerChannel | tl_types.InputPeerUser
type ThisInputSender = tl_types.InputPeerUser | tl_types.InputChannel

type RuleCallback = Callable[..., Awaitable[str | None]]

class ParameterType(ABC):
    """
    Computes the value of a rule argument based on its type hint.
    """

    @abstractmethod
    def matches(self, parameter: inspect.Parameter) -> bool: ...

    @abstractmethod
    async def get_value(self, event: EventCommon): ...

    @abstractmethod
    def validate(self, parameter: inspect.Parameter, event: EventBuilder): ...


class EventParameterType(ParameterType):
    def matches(self, parameter: inspect.Parameter) -> bool:
        return issubclass(parameter.annotation, EventCommon) or parameter.annotation is Message

    async def get_value(self, event: EventCommon):
        return event

    def validate(self, parameter: inspect.Parameter, event: EventBuilder):
        if (isinstance(event, events.NewMessage | events.ChatAction)
                and parameter.annotation is not event.Event
                and parameter.annotation is not Message):
            raise FoldsRuleArgumentException(f'Invalid argument type for {event}. Try using `folds.Message`.')


class TextParameterType(ParameterType):
    def matches(self, parameter: inspect.Parameter) -> bool:
        return parameter.annotation is str

    async def get_value(self, event: Message):
        return event.raw_text

    def validate(self, parameter: inspect.Parameter, event: EventBuilder):
        if not isinstance(event, events.NewMessage):
            raise FoldsRuleArgumentException('Text argument can be used only with new message events.')


class ChatParameterType(ParameterType, ABC):
    def matches(self, parameter: inspect.Parameter) -> bool:
        return parameter.annotation == ChatGetter


class ReplyToParameterType(ParameterType):
    def matches(self, parameter: inspect.Parameter) -> bool:
        return parameter.annotation is ThisReplyTo

    async def get_value(self, event: Message):
        return await event.get_reply_message()

    def validate(self, parameter: inspect.Parameter, event: EventBuilder):
        if not isinstance(event, events.NewMessage):
            raise FoldsRuleArgumentException('ReplyTo argument can be used only with new message events.')


class SimpleMethodParameterType(ParameterType):
    def __init__(self, method_name: str, type_):
        self.method_name = method_name
        self.type = type_

    def matches(self, parameter: inspect.Parameter) -> bool:
        return parameter.annotation is self.type

    async def get_value(self, event: Message):
        method = getattr(event, self.method_name)
        return await method()

    def validate(self, parameter: inspect.Parameter, event: EventBuilder):
        pass


parameter_types: tuple[ParameterType, ...] = (
    TextParameterType(),
    ReplyToParameterType(),
    SimpleMethodParameterType('get_chat', ThisChat),
    SimpleMethodParameterType('get_sender', ThisSender),
    SimpleMethodParameterType('get_input_chat', ThisInputChat),
    SimpleMethodParameterType('get_input_sender', ThisInputSender),
    EventParameterType(),
)
