import asyncio

from folds import Skill, Message, SystemMessage
from telethon import Button

from avatar_emoji_bot.functions import update_or_create_set
from avatar_emoji_bot.utils import get_chat_set_link

skill = Skill()
lock = asyncio.Lock()


@skill.added_to_group()
async def f(event: SystemMessage):
    await event.respond('Creating an emoji pack...')

    user_id = event.original_update.new_participant.inviter_id
    async with lock:
        is_created = await update_or_create_set(event.chat, user_id)

    if is_created:
        return f'Created!\n{get_chat_set_link(event)}'
    else:
        return f'Pack updated!\n{get_chat_set_link(event)}'


@skill.group_commands.update()
async def f(message: Message):
    info_message = await message.respond('Updating the emoji pack...')

    async with lock:
        await update_or_create_set(message.chat, message.sender_id)

    await info_message.reply(f'Emoji pack updated!\n{get_chat_set_link(message)}')


@skill.private_message()
async def f(message: Message):
    button = Button.url('Choose group', f't.me/{message.client.me.username}?startgroup')
    await message.respond('Hello! Add me to group to start.', buttons=button)
