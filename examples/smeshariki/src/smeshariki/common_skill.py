from folds import Skill

common_skill = Skill()

@common_skill.private_message
async def f():
    return 'Hi!'
