from collections.abc import Callable
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App

type Lifespan[T] = Callable[[T], AbstractAsyncContextManager]


@asynccontextmanager
async def default_lifespan(app: 'App'):
    yield
