from folds import App
from folds.admin import SimpleAdmin
from smeshariki.settings import Settings

settings = Settings()

app = App(
    settings.api_id,
    settings.api_hash,
    # connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
    # proxy=('80.211.160.148', 14443, '7316c4fbc53fb9f4e6784f2a68c01461'),
    admin=SimpleAdmin(user_ids=[254210206]),
)

ezhik_bot = app.create_bot(settings.ezhik_bot_token)
barash_bot = app.create_bot(settings.barash_bot_token)
losyash_bot = app.create_bot(settings.losyash_bot_token)
