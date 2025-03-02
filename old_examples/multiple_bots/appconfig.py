from dataclasses import dataclass

from folds import BotInApp


@dataclass
class AppBots:
    first: BotInApp
    second: BotInApp
    third: BotInApp
