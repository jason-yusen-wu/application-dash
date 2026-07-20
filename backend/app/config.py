from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    anthropic_api_key: str
    google_client_id: str = ""
    google_client_secret: str = ""
    session_secret: str = "change-me"
    backend_base_url: str = "http://localhost:8000"


settings = Settings()
