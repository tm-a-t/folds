import folds
from folds.context.context_var_wrapper import ContextVarWrapper

bot: ContextVarWrapper['folds.BotInApp'] = ContextVarWrapper("bot")
