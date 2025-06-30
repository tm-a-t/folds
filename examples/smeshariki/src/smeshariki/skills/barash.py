from folds import Skill
from smeshariki.strings import all_bot_strings

barash_skill = Skill()


@barash_skill.added_to_group()
async def _():
    return all_bot_strings.barash.greeting
