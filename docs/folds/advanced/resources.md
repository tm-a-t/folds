# App Resources

## Context

To quickly access common variables across the app, store a typed context object:

```python
class ExampleBotContext:
    database = ...


bot = Bot(context=ExampleBotContext())


# Example usage
@bot.private_message
async def answer():
    db = bot.context.database
    ...
```

## Lifecycle

You can pass `lifespan` to add logic before and after the bot runs.

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(bot_app):
    print('Open resources')
    try:
        yield
    finally:
        print('Close resources')


bot = Bot(lifespan=lifespan)
...
```

