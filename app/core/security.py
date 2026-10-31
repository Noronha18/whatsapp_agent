import logging

from fastapi import HTTPException, Request
from twilio.request_validator import RequestValidator

from app.core.config import settings

logger = logging.getLogger(__name__)
_validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)


def mask_number(number: str) -> str:
    """Oculta o número nos logs: whatsapp:+5581999991234 -> whatsapp:+55*******1234."""
    prefix, _, digits = number.rpartition("+")
    if len(digits) <= 6:
        return "***"
    return f"{prefix}+{digits[:2]}{'*' * (len(digits) - 6)}{digits[-4:]}"


async def verify_twilio_signature(request: Request) -> None:
    """Rejeita requisições que não foram assinadas pela Twilio com o nosso Auth Token."""
    if not settings.VALIDATE_TWILIO_SIGNATURE:
        return

    signature = request.headers.get("X-Twilio-Signature", "")
    url = settings.PUBLIC_WEBHOOK_URL or str(request.url)
    form = await request.form()
    params = {key: value for key, value in form.items()}

    if not signature or not _validator.validate(url, params, signature):
        logger.warning("Webhook rejeitado: assinatura Twilio inválida")
        raise HTTPException(status_code=403, detail="Invalid signature")


def is_authorized(sender: str) -> bool:
    """Somente números da allowlist podem consultar dados. Lista vazia = ninguém autorizado."""
    return sender in settings.allowed_numbers
