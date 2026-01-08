from groq import Groq
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repositories.conversation_repository import ConversationRepository

# Cliente nativo da Groq
client = Groq(api_key=settings.GROQ_API_KEY)

def get_groq_response(user_message: str, wa_id: str, name: str, db: Session) -> str:
    """
    Processa a mensagem, salva no histórico e retorna a resposta da IA.
    """
    # 1. Inicializa o repositório
    repo = ConversationRepository(db)

    # 2. Salva a mensagem do usuário no banco (MEMÓRIA)
    # Aqui salvamos ANTES de enviar, para garantir que se der erro na IA, sua pergunta ficou salva
    repo.add_message(wa_id=wa_id, name=name, role="user", content=user_message)

    # 3. Busca o histórico recente (CONTEXTO)
    # Pegamos as últimas 10 mensagens para ele ter um bom contexto
    history = repo.get_history(wa_id=wa_id, limit=10)

    # 4. Define a Personalidade (System Prompt)
    system_prompt = (
        "Você é um assistente pessoal útil e direto chamado Jarvis. "
        "Responda em português do Brasil. Seja conciso."
    )

    # 5. Monta a lista de mensagens para a Groq
    messages_payload = [{"role": "system", "content": system_prompt}]

    # Adiciona o histórico recuperado do banco
    for msg in history:
        messages_payload.append({"role": msg.role, "content": msg.content})

    try:
        # 6. Chama a IA
        chat_completion = client.chat.completions.create(
            messages=messages_payload,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300 # Aumentei um pouco para ele poder explicar código se precisar
        )

        ai_response = chat_completion.choices[0].message.content

        # 7. Salva a resposta da IA no banco (MEMÓRIA)
        repo.add_message(wa_id=wa_id, name=name, role="assistant", content=ai_response)

        return ai_response

    except Exception as e:
        print(f"Erro na Groq: {e}")
        return "Oss! Meu cérebro deu uma travada no tatame. Tente novamente."