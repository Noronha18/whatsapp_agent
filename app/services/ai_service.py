# app/services/ai_service.py
import os
from dotenv import load_dotenv
from groq import Groq
from app.repositories.conversation_repository import get_history, add_message
from app.services.tools_service import consultar_pagamento_aluno

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Você é assistente de academia que usa DADOS REAIS da Tool.

## REGRAS PAGAMENTOS (OBRIGATÓRIO):
1. Quando receber [SISTEMA] SYSTEM_DATA: → COPIE OS DADOS EXATOS
2. NUNCA invente valores, datas ou status
3. Se Tool disser "Não encontrei" → informe isso
4. Sempre mencione: valor, data e status da Tool

EXEMPLO CORRETO:
[SISTEMA] SYSTEM_DATA: Último pagamento de Priscila Ingrid: - Data: 06/01/2026 - Valor: R$ 550.00
→ "O último pagamento de Priscila Ingrid foi R$550 em 06/01/2026 (Aprovado)"

SEMPRE priorize [SISTEMA] sobre qualquer conhecimento anterior.
"""



def get_groq_response(message_body: str, profile_name: str, phone_number: str) -> str:
    add_message(phone_number, "user", message_body, profile_name)

    contexto_extra = ""
    msg_lower = message_body.lower()


    if any(palavra in msg_lower for palavra in ["pagamento", "mensalidade", "deve", "status financeiro"]):
        print("🔍 [DEBUG] Gatilho de pagamento detectado!")

        extract_prompt = f"""
        Da frase: "{message_body}"
        Extraia APENAS o nome da pessoa mencionada (ex: "Adriana Silva", "João").
        Se não tiver nome claro, responda "NOME_NAO_IDENTIFICADO".
        Responda com APENAS o nome, sem explicação.
        """

        extract_comp = client.chat.completions.create(
            messages=[{"role": "user", "content": extract_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0
        )
        nome = extract_comp.choices[0].message.content.strip()
        print(f"🔍 [DEBUG] Nome extraído: '{nome}'")

        if nome and "NOME_NAO_IDENTIFICADO" not in nome:
            print("🔍 [DEBUG] Chamando Tool...")
            dados = consultar_pagamento_aluno(nome)
            print(f"🔍 [DEBUG] Tool retornou: {dados[:100]}...")
            contexto_extra = f"\n\n[SISTEMA] {dados}"
        else:
            print("🔍 [DEBUG] Nome não identificado.")

    history = get_history(phone_number)
    messages = [{"role": "system", "content": SYSTEM_PROMPT + contexto_extra}]

    for msg in history:
        role = "user" if msg.role == "user" else "assistant"
        messages.append({"role": role, "content": msg.content})

    messages.append({"role": "user", "content": message_body})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.7
    )

    ai_reply = chat_completion.choices[0].message.content
    add_message(phone_number, "assistant", ai_reply, profile_name)
    return ai_reply
