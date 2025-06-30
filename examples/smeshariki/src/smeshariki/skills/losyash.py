from folds import Skill
from smeshariki.strings import all_bot_strings

losyash_skill = Skill()


@losyash_skill.added_to_group()
async def _():
    return all_bot_strings.losyash.greeting
