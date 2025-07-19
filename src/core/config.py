from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_url: str
    redis_url: str

    tg_token: str
    admin_tg_id: int


settings = Settings()
