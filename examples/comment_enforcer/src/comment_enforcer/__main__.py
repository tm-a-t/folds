import logging

from dotenv import load_dotenv
from telethon.errors import MessageDeleteForbiddenError
from telethon.tl.functions.ephemeral import SendMessageRequest

from folds import Bot, Message

logging.basicConfig(
    format='%(asctime)s    %(levelname)s  %(message)s    %(pathname)s:%(lineno)d',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)

load_dotenv()
bot = Bot(parse_mode='html')

explanation_text = ('Привет, в этом чате можно писать только ответы на другие сообщения '
                    '(так читатели комментариев ничего не пропустят). '
                    'Я удалил твоё сообщение, можешь скопировать его и отправить ответом:')


@bot.private_message
async def f():
    return 'Добавьте меня в чат канала, чтобы я начал удалять сообщения вне комментариев'


@bot.group_message
async def f(message: Message):
    if message.action:
        return None
    if await is_in_thread(message):
        return None

    try:
        await message.delete()
    except MessageDeleteForbiddenError:
        return 'Привет. Админы чата, сделайте меня админом и разрешите удалять сообщения, чтобы я начал работать'

    # At the time of writing, normal message sending functions don't support ephemeral messages
    await bot(SendMessageRequest(message.chat_id, message.sender_id, explanation_text))
    await bot(SendMessageRequest(
        message.chat_id,
        message.sender_id,
        message.raw_text,
        None,
        message.entities,
        message.media,
        None,
        message.rich_message,
    ))

    return None


async def is_in_thread(message: Message):
    if not message.reply_to:
        return False

    root_id = message.reply_to.reply_to_top_id or message.reply_to.reply_to_msg_id
    root: Message = await bot.get_messages(message.chat_id, ids=root_id)
    fwd_from = root.fwd_from
    return not fwd_from or not fwd_from.saved_from_peer == fwd_from.from_id == root.from_id is not None


bot.run()
