from telethon.events import ChatAction as _ChatAction
from telethon.events import InlineQuery as _InlineQuery
from telethon.tl.custom import Message as _Message

from folds.app.app import App
from folds.app.bot import Bot
from folds.app.bot_in_app import BotInApp
from folds.app.skill import Skill
from folds.rules.parameter_types import ThisChat, ThisInputChat, ThisInputSender, ThisReplyTo, ThisSender

Message = _Message
SystemMessage = _ChatAction.Event
Query = _InlineQuery.Event

__all__ = [
    'Bot',
    'App',
    'BotInApp',
    'Skill',
    'Message',
    'SystemMessage',
    'Query',
    'ThisReplyTo',
    'ThisChat',
    'ThisSender',
    'ThisInputChat',
    'ThisInputSender',
]
