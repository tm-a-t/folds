from typing import TYPE_CHECKING, cast

from .vars import bot as bot_wrapper

if TYPE_CHECKING:
    import folds

bot: 'folds.BotInApp' = cast('folds.BotInApp', bot_wrapper)
"""If used in a rule, this is the current bot."""

__all__ = ['bot']
