from dataclasses import dataclass

from folds import BotInApp


@dataclass
class AppConfig:
    first: BotInApp
    second: BotInApp
    third: BotInApp
