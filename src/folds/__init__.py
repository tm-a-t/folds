from folds.app.bot_in_app import BotInApp
from folds.app.app import App
from folds.app.bot import Bot
from folds.app.skill import Skill
from telethon.tl.custom import Message as _Message
from telethon.events import ChatAction as _ChatAction
from folds.rules.parameter_types import UseReplyTo, UseChat, UseSender, UseInputChat, UseInputSender

Message = _Message
SystemMessage = _ChatAction.Event
