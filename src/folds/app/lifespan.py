from contextlib import asynccontextmanager
from typing import Callable, AsyncContextManager, Any

type Lifespan[T] = Callable[[T], AsyncContextManager]

@asynccontextmanager
async def default_lifespan(app: Any):
    yield
