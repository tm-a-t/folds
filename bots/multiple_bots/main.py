from bots.multiple_bots.appconfig import AppBots
from folds import BotInApp
from folds.app.app import App

# bots = AppBots(
#     first=None,
#     second=22,
# )

app = App(
    111,
    "111",
    bots=bots,
)

app.bots = AppBots(
    first=app.bot('aaa')
)
