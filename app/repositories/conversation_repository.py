from sqlalchemy.orm import Session
from app.models.conversations import Conversation
from app.core.database import SessionLocal # Precisamos criar sessões manuais se não vier da rota

# --- Funções "Soltas" (Clean & Simple) ---

def add_message(wa_id: str, role: str, content: str, name: str = "User"):
    """
    Salva uma mensagem criando uma nova sessão de banco rápida.
    Nota: Em projetos maiores, injetaríamos a sessão, mas aqui simplifica o AI Service.
    """
    db = SessionLocal() # Abre conexão
    try:
        message = Conversation(
            wa_id=wa_id,
            name=name,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    finally:
        db.close() # Fecha conexão (Importante!)

def get_history(wa_id: str, limit: int = 5):
    """Busca histórico usando sessão descartável."""
    db = SessionLocal()
    try:
        messages = (
            db.query(Conversation)
            .filter(Conversation.wa_id == wa_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
        # Retorna invertido (Cronológico)
        return messages[::-1]
    finally:
        db.close()
