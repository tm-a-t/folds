from folds import Skill, Message

pm_skill = Skill()


@pm_skill.private_message()
async def private(event: Message):
    await event.reply("okay")
