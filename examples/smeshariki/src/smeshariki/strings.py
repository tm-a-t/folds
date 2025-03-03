from typing import Type, Tuple

from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, YamlConfigSettingsSource


class BotStrings(BaseModel):
    name: str
    greeting: str
    phrases: dict[str, str]


class AllBotStrings(BaseSettings):
    ezhik: BotStrings
    barash: BotStrings
    losyash: BotStrings


    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls, 'strings.yml'),)


all_bot_strings = AllBotStrings()
