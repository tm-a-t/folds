import folds
from folds.app.bot_client import BotClient
from folds.context.context_var_wrapper import ContextVarWrapper

client: ContextVarWrapper[BotClient] = ContextVarWrapper("client")
bot: ContextVarWrapper['folds.BotInApp'] = ContextVarWrapper("bot")
