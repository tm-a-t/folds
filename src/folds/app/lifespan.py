from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from typing_extensions import AsyncContextManager

if TYPE_CHECKING:
    from .app import App

type Lifespan[T] = Callable[[T], AsyncContextManager]


@asynccontextmanager
async def default_lifespan(app: 'App'):
    yield
