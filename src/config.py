from pydantic_settings import BaseSettings, SettingsConfigDict


# This is a configuration file for a FastAPI application using Pydantic for settings management. Read into .env file.
class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


settings = Settings()
