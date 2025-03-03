from contextlib import contextmanager
from contextvars import ContextVar

from folds.exceptions import FoldsVariableException


class ContextVarWrapper[T]:
    """
    Sets the values of context variables in rules.
    """

    def __init__(self, name: str):
        self.context_var: ContextVar[T] = ContextVar(name)

    @contextmanager
    def using(self, value: T):
        token = self.context_var.set(value)
        yield
        self.context_var.reset(token)

    def _try_getting_value(self) -> T:
        try:
            return self.context_var.get()
        except LookupError:
            raise FoldsVariableException(
                f"Variable '{self.context_var.name}' not found. It can only be used in rule functions."
            )

    def __getattr__(self, item):
        return getattr(self._try_getting_value(), item)

    def __call__(self, *args, **kwargs):
        return self._try_getting_value()(*args, **kwargs)
