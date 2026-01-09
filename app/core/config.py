from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    DATABASE_URL: str
    PERSONAL_DB_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
