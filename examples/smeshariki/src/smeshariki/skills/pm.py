from folds import Message, Skill

pm_skill = Skill()


@pm_skill.private_message
async def private(event: Message):
    await event.reply('okay')
