from folds import Logic

common_logic = Logic()

@common_logic.private_message
async def f():
    return 'Hi!'
