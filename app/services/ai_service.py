# app/services/ai_service.py
import os
import json
from dotenv import load_dotenv
from groq import Groq

from app.repositories.conversation_repository import get_history, add_message
from app.services.tools_service import consultar_pagamento_aluno, lista_alunos

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Você é um assistente de academia útil e amigável.
Você tem acesso a ferramentas para consultar dados reais de alunos e pagamentos.

Ao usar uma ferramenta, você receberá os dados em formato de texto.
Use esses dados para responder à pergunta do usuário de forma natural.

Se a ferramenta retornar que não encontrou dados, informe isso ao usuário educadamente.
Não invente dados que não foram fornecidos pelas ferramentas.
"""

# Definição das ferramentas disponíveis para o modelo
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_pagamento_aluno",
            "description": "Consulta o último pagamento de um aluno pelo nome",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_aluno": {
                        "type": "string",
                        "description": "Nome do aluno para consultar o pagamento"
                    }
                },
                "required": ["nome_aluno"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lista_alunos",
            "description": "Lista todos os alunos cadastrados na academia",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Mapeamento de nomes de funções para as funções reais
AVAILABLE_FUNCTIONS = {
    "consultar_pagamento_aluno": consultar_pagamento_aluno,
    "lista_alunos": lista_alunos
}

def get_groq_response(message_body: str, profile_name: str, phone_number: str) -> str:
    # 1. Salva mensagem do usuário
    add_message(phone_number, "user", message_body, profile_name)

    # 2. Prepara histórico de mensagens
    history = get_history(phone_number)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history:
        role = "user" if msg.role == "user" else "assistant"
        # Filtra mensagens de tool calls antigas se necessário, ou apenas adiciona texto
        if msg.content:
            messages.append({"role": role, "content": msg.content})

    # Adiciona a mensagem atual
    messages.append({"role": "user", "content": message_body})

    # 3. Primeira chamada ao modelo (pode decidir usar tools)
    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        tools=TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 4. Se o modelo decidiu chamar ferramentas
    if tool_calls:
        # Adiciona a mensagem do assistente com os tool_calls ao histórico da conversa atual
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
            
            if function_to_call:
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"[DEBUG] Chamando tool: {function_name} com args: {function_args}")
                
                # Chama a função real
                if function_name == "lista_alunos":
                    function_response = function_to_call()
                else:
                    function_response = function_to_call(**function_args)
                
                # Adiciona a resposta da ferramenta às mensagens
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        # 5. Segunda chamada ao modelo (com as respostas das tools)
        second_response = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile"
        )
        ai_reply = second_response.choices[0].message.content
    else:
        # Se não houve tool calls, usa a resposta direta
        ai_reply = response_message.content

    # 6. Salva e retorna a resposta final
    add_message(phone_number, "assistant", ai_reply, profile_name)
    return ai_reply
