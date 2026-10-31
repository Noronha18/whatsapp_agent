from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # IA
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str  # ex.: whatsapp:+14155238886

    # Segurança do webhook
    # URL pública exata configurada no console da Twilio (ex.: https://xxxx.ngrok-free.app/whatsapp).
    # Necessária para validar a assinatura quando a app roda atrás de túnel/proxy.
    PUBLIC_WEBHOOK_URL: str | None = None
    VALIDATE_TWILIO_SIGNATURE: bool = True
    # Números autorizados a conversar com o agente, separados por vírgula (ex.: whatsapp:+5581999999999)
    ALLOWED_NUMBERS: str = ""

    # Bancos
    DATABASE_URL: str  # histórico de conversas do agente
    PERSONAL_DB_URL: str  # base do PTRoster (somente leitura)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("ALLOWED_NUMBERS")
    @classmethod
    def _normalize(cls, v: str) -> str:
        return ",".join(n.strip() for n in v.split(",") if n.strip())

    @property
    def allowed_numbers(self) -> set[str]:
        return set(self.ALLOWED_NUMBERS.split(",")) if self.ALLOWED_NUMBERS else set()


settings = Settings()
