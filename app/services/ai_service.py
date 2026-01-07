from openai import OpenAI
from app.core.config import settings
# --- DEBUG ---
print(f"DEBUG: Chave Groq Configurada? {'SIM' if settings.GROQ_API_KEY else 'NÃO'}")
# Vamos ver os primeiros 4 caracteres para confirmar que não pegou a da OpenAI por engano
print(f"DEBUG: Prefixo da Chave: {settings.GROQ_API_KEY[:4] if settings.GROQ_API_KEY else 'VAZIO'}")
# -------------

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.GROQ_API_KEY.strip())

def get_ai_response(user_message:str) -> str:
    """
    Envia a mensagem do usuario para o GPT e retorna a resposta
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é um mentor Sênior de Python e Judoca. Responda de forma curta e direta (máximo 50 palavras)."},
                {"role": "user", "content": user_message},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na OpenAI:{e}")
        return "Desculpe, meu cerebro esta temporariamente fora do ar."