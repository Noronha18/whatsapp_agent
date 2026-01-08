from fastapi import FastAPI, Form, Depends, Response
from typing import Annotated
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

# IMPORTANTE: Estamos importando get_groq_response
from app.core.database import get_db, Base, engine
from app.services.ai_service import get_groq_response

# Garante que as tabelas existam
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "Active", "Version": "2.0 (Com Memória)"}

@app.post("/whatsapp")
async def reply_whatsapp(
    Body: Annotated[str, Form()],
    From: Annotated[str, Form()],
    ProfileName: Annotated[str, Form()] = "Usuário",
    db: Session = Depends(get_db)
):
    print(f"📩 Mensagem recebida de {ProfileName} ({From}): {Body}")

    ai_reply = get_groq_response(
        user_message=Body,
        wa_id=From,
        name=ProfileName,
        db=db
    )

    resp = MessagingResponse()
    resp.message(ai_reply)

    # A MUDANÇA ESTÁ AQUI:
    # Retornamos explicitamente como XML
    return Response(content=str(resp), media_type="application/xml")