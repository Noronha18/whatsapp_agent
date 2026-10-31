import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Response
from fastapi.concurrency import run_in_threadpool
from twilio.rest import Client

from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import is_authorized, mask_number, verify_twilio_signature
from app.services.ai_service import FALLBACK_REPLY, get_groq_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if not settings.allowed_numbers:
        logger.warning("ALLOWED_NUMBERS vazio: o agente não responderá a ninguém.")
    yield


app = FastAPI(title="WhatsApp Agent", lifespan=lifespan)
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/whatsapp", dependencies=[Depends(verify_twilio_signature)])
async def reply_whatsapp(
    Body: Annotated[str, Form()],
    From: Annotated[str, Form()],
    ProfileName: Annotated[str, Form()] = "Usuário",
):
    if not is_authorized(From):
        # Não responde nem revela que o número existe; só registra de forma mascarada.
        logger.warning("Mensagem ignorada de número não autorizado: %s", mask_number(From))
        return Response(content=EMPTY_TWIML, media_type="application/xml")

    logger.info("Mensagem recebida de %s", mask_number(From))

    # Chamadas síncronas (Groq, SQLAlchemy) fora do event loop
    try:
        ai_reply = await run_in_threadpool(
            get_groq_response, message_body=Body, profile_name=ProfileName, phone_number=From
        )
    except Exception:
        logger.exception("Falha ao gerar resposta")
        ai_reply = FALLBACK_REPLY

    try:
        msg = await run_in_threadpool(
            twilio_client.messages.create, from_=settings.TWILIO_PHONE_NUMBER, body=ai_reply, to=From
        )
        logger.info("Resposta enviada (SID %s)", msg.sid)
    except Exception:
        logger.exception("Falha ao enviar mensagem pela Twilio")

    return Response(content=EMPTY_TWIML, media_type="application/xml")
