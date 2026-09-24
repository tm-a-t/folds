from smeshariki.strings import all_bot_strings

from folds import Skill

losyash_skill = Skill()


@losyash_skill.added_to_group
async def _():
    return all_bot_strings.losyash.greeting
