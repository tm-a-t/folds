import logging
import os

from dotenv import load_dotenv
from folds import Bot, Message
from telethon import events, Button
from telethon.errors import ChatAdminRequiredError, MessageIdInvalidError, InlineBotRequiredError

logging.basicConfig(
    format='%(asctime)s    %(levelname)s  %(message)s    %(pathname)s:%(lineno)d',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)

load_dotenv()
bot = Bot(parse_mode='html')

@bot.private_message
async def f():
    return 'Please add me to a channel first!'

@bot.channel_message
async def f(message: Message):
    try:
        await bot.edit_message(message.chat_id, message.id, buttons=Button.inline('✔️ Mark as done', 'complete'))
    except (ChatAdminRequiredError, MessageIdInvalidError, InlineBotRequiredError):
        # Bot is not an admin, or the message is uneditable (for example, a sticker)
        pass

@bot.on(events.CallbackQuery())
async def f(event: events.CallbackQuery.Event):
    message = await event.get_message()
    source: str | None = message.text
    if event.data == b'complete':
        text = f'✅ <del>{source}</del>' if source else '✅'
        button = Button.inline('Mark as undone', 'uncomplete')
        await event.edit(text, buttons=button, parse_mode='html')
    elif event.data == b'uncomplete':
        text = source.removeprefix('✅ ').removeprefix('<del>').removesuffix('</del>') if source else None
        button = Button.inline('✔️ Mark as done', 'complete')
        await event.edit(text, buttons=button, parse_mode='html')


bot.run()
