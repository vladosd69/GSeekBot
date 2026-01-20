import urllib.parse

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MONGO_")

    HOST: str
    PORT: int
    USER: str
    PASSWORD: SecretStr
    NAME: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    COMPOSE_PROJECT_NAME: str
    BOT_TOKEN: SecretStr

    MONGO: MongoSettings = MongoSettings()

    @property
    def mongo_dsn(self) -> str:
        return "mongodb://{user}:{password}@{host}:{port}".format(  # noqa: UP032
            user=self.MONGO.USER,
            password=urllib.parse.quote(self.MONGO.PASSWORD.get_secret_value()),
            host=self.MONGO.HOST,
            port=self.MONGO.PORT,
        )

settings = Settings()
