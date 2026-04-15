from typing import TYPE_CHECKING

from .vars import bot

if TYPE_CHECKING:
    import folds

bot: 'folds.BotInApp'
"""If used in a rule, this is the current bot."""

__all__ = ['bot']
