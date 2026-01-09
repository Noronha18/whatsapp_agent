# app/services/tools_service.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("PERSONAL_DB_URL")
engine = create_engine(DB_URL)


def consultar_pagamento_aluno(nome_aluno: str) -> str:
    print(f"🥋 [TOOL] Buscando dados para: {nome_aluno}...")

    try:
        with engine.connect() as conn:
            # Encontra aluno
            query_aluno = text("SELECT id, nome FROM alunos WHERE nome ILIKE :nome LIMIT 1")
            result_aluno = conn.execute(query_aluno, {"nome": f"%{nome_aluno}%"}).fetchone()

            if not result_aluno:
                return f"SYSTEM_DATA: Não encontrei aluno com nome '{nome_aluno}'."

            aluno_id = result_aluno.id
            aluno_nome_real = result_aluno.nome

            # Último pagamento
            query_pagto = text("""
                               SELECT data_pagamento, valor
                               FROM pagamentos
                               WHERE aluno_id = :aid
                               ORDER BY data_pagamento DESC LIMIT 1
                               """)
            result_pagto = conn.execute(query_pagto, {"aid": aluno_id}).fetchone()

            if result_pagto:
                data_fmt = result_pagto.data_pagamento.strftime('%d/%m/%Y')
                return (
                    f"SYSTEM_DATA: Último pagamento de {aluno_nome_real}:\n"
                    f"- Data: {data_fmt}\n"
                    f"- Valor: R$ {result_pagto.valor:.2f}\n"
                    f"- Status: Aprovado"
                )
            else:
                return f"SYSTEM_DATA: {aluno_nome_real} não tem pagamentos."

    except Exception as e:
        return f"SYSTEM_ERROR: {str(e)}"
