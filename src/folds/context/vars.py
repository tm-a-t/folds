from typing import TYPE_CHECKING

from folds.context.context_var_wrapper import CallableContextVarWrapper

if TYPE_CHECKING:
    import folds

bot: CallableContextVarWrapper['folds.BotInApp'] = CallableContextVarWrapper("bot")
