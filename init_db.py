from app.core.database import Base, engine
from app.models.conversations import Conversation

print("Criando tabelas...")

try:
    Base.metadata.create_all(bind=engine)
    print("Criando tabelas com sucesso...")
except Exception as e:
    print(f"❌ Erro ao conectar no banco: {e}")