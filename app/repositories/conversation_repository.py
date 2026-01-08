from sqlalchemy.orm import Session
from app.models.conversations import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, wa_id: str, name: str, role: str, content: str):
        """Salva uma nova mensagem no banco."""
        message = Conversation(
            wa_id=wa_id,
            name=name,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_history(self, wa_id: str, limit: int = 5):
        """
        Busca as últimas 'limit' mensagens desse usuário.
        Retorna do mais antigo para o mais novo (cronológico).
        """
        # 1. Pega as últimas X mensagens (ordenadas por mais recente primeiro)
        messages = (
            self.db.query(Conversation)
            .filter(Conversation.wa_id == wa_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )

        # 2. Inverte a lista para ficar na ordem cronológica (Passado -> Presente)
        return messages[::-1]
