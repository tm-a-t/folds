import logging

from folds import Skill, Message, SystemMessage, ThisReplyTo, ThisChat
from smeshariki.app import ezhik_bot, barash_bot, losyash_bot

from smeshariki.openai_client import ask
from smeshariki.strings import all_bot_strings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

ezhik_skill = Skill()
last_quote_usage: dict[tuple[int, int], datetime] = {}



@ezhik_skill.added_to_group()
async def _():
    return all_bot_strings.ezhik.greeting


@ezhik_skill.group_message()
async def _(message: Message, reply_to: ThisReplyTo):
    name: str | None = None
    if reply_to:
        name = {
            ezhik_bot._client.me.id: 'Ёжик',
            barash_bot._client.me.id: 'Бараш',
            losyash_bot._client.me.id: 'Лосяш',
        }.get(reply_to.sender_id)

    if name is None and len(message.raw_text or '') < 8 or len(message.raw_text) < 3:
        return

    if name is None:
        text = message.raw_text
    else:
        text = f'(in reply to {name}) {message.raw_text}'

    result = await ask(text)
    logger.info('Group %s, message %s --> %s', message.chat_id, message.id, result)

    for strings, bot in (all_bot_strings.ezhik, ezhik_bot), (all_bot_strings.barash, barash_bot), (all_bot_strings.losyash, losyash_bot):
        for trigger in strings.phrases:
            if result.get(trigger) is True:
                condition = message.chat_id, trigger
                last_time = last_quote_usage.get(condition)
                if last_time and datetime.now() - last_time < timedelta(days=1):
                    logger.info('Ignored recently used trigger: %s', trigger)
                else:
                    logger.info('Using trigger: %s', trigger)
                    last_quote_usage[condition] = datetime.now()
                    await bot._client.send_message(message.chat_id, strings.phrases[trigger], reply_to=message.id)
                    break
