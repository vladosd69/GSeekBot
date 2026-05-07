from __future__ import annotations

import urllib.parse

from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    HOST: str
    PORT: int
    USER: str
    PASSWORD: SecretStr
    NAME: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", extra="ignore", hide_input_in_errors=True
    )

    BOT_TOKEN: SecretStr

    MONGO: MongoSettings

    @property
    def mongo_dsn(self) -> str:
        return "mongodb://{user}:{password}@{host}:{port}".format(  # noqa: UP032
            user=self.MONGO.USER,
            password=urllib.parse.quote(self.MONGO.PASSWORD.get_secret_value()),
            host=self.MONGO.HOST,
            port=self.MONGO.PORT,
        )
