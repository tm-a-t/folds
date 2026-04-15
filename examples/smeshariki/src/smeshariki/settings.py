from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api: str

    ezhik_bot_token: str
    barash_bot_token: str
    losyash_bot_token: str

    model_config = SettingsConfigDict(env_file='.env')
