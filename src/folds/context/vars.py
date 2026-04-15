from typing import TYPE_CHECKING

from folds.context.context_var_wrapper import ContextVarWrapper

if TYPE_CHECKING:
    import folds

bot: ContextVarWrapper['folds.BotInApp'] = ContextVarWrapper("bot")
