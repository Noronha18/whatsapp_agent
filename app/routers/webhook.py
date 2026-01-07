from fastapi import Depends, APIRouter, Form, Response, Depends, Request
from twilio.twiml.messaging_response import MessagingResponse
from app.core.config import settings

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
        From: str = Form(...),
        Body: str = Form(...),
):
    print(f"📥 Recebido de {From}: {Body}")

    resp = MessagingResponse()

    msg_response = f"Olá! Você disse: {Body}"
    resp.message(msg_response)

    return Response(content=str(resp), media_type="application/xml")