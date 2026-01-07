from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()