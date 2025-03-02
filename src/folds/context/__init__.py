from folds.context.context_var_wrapper import ContextVarWrapper
from .vars import client, bot
import folds
from folds.app.bot_client import BotClient

client: BotClient
"""If used in a rule, this is the current Telegram client."""
bot: 'folds.BotInApp'
"""If used in a rule, this is the current bot."""
