from folds.app.bot_in_app import BotInApp
from folds.app.app import App
from folds.app.bot import Bot
from folds.app.skill import Skill
from telethon.tl.custom import Message as _Message
from telethon.events import ChatAction as _ChatAction, InlineQuery as _InlineQuery
from folds.rules.parameter_types import ThisReplyTo, ThisChat, ThisSender, ThisInputChat, ThisInputSender

Message = _Message
SystemMessage = _ChatAction.Event
Query = _InlineQuery.Event
