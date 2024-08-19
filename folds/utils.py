import inspect
from typing import Any


async def await_if_needed(value: Any):
    return await value if inspect.isawaitable(value) else value
