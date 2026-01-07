from fastapi import FastAPI
from app.routers import webhook

app = FastAPI(title="Agente Whatsapp - Noronha")

app.include_router(webhook.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "O Agente está vivo"}