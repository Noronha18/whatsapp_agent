from fastapi import FastAPI, Form, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from twilio.rest import Client 

from app.core.database import get_db, Base, engine
from app.services.ai_service import get_groq_response
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Inicializa o cliente Twilio
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

@app.get("/")
def read_root():
    return {"Status": "Active", "Version": "3.0 (Active Sender)"}

@app.post("/whatsapp")
async def reply_whatsapp(
    Body: Annotated[str, Form()],
    From: Annotated[str, Form()],
    ProfileName: Annotated[str, Form()] = "Usuário",
    db: Session = Depends(get_db)
):
    print(f"📩 Recebido de {ProfileName}: {Body}")

    # 1. Gera resposta (pode demorar alguns segundos)
    ai_reply = get_groq_response(
        user_message=Body,
        wa_id=From,
        name=ProfileName,
        db=db
    )

    # 2. Envio Ativo
    try:
        msg = twilio_client.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            body=ai_reply,
            to=From
        )
        print(f"✅ Enviado via Twilio API. SID: {msg.sid}")
    except Exception as e:
        print(f"❌ Erro ao enviar pro Twilio: {e}")

    return "OK"
