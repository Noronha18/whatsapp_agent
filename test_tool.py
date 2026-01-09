import os
from sqlalchemy import create_engine, text, engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

def consultar_pagamento_aluno(nome_aluno: str) -> str:
    print(f"🥋 [TOOL] Buscando dados para: {nome_aluno}...")

    try:
        with engine.connect() as conn:
            # Query 1: Aluno (named parameter)
            query_aluno = text("SELECT id, nome FROM alunos WHERE nome ILIKE :nome LIMIT 1")
            result_aluno = conn.execute(query_aluno, {"nome": f"%{nome_aluno}%"}).fetchone()

            if not result_aluno:
                return f"SYSTEM_DATA: Não encontrei aluno com nome '{nome_aluno}'."

            aluno_id = result_aluno.id
            aluno_nome_real = result_aluno.nome

            # Query 2: Pagamentos (named parameter)
            query_pagto = text("""
                               SELECT data_pagamento, valor
                               FROM pagamentos
                               WHERE aluno_id = :aid
                               ORDER BY data_pagamento DESC LIMIT 1
                               """)
            result_pagto = conn.execute(query_pagto, {"aid": aluno_id}).fetchone()

            if result_pagto:
                data_fmt = (
                    result_pagto.data_pagamento.strftime('%d/%m/%Y')
                    if hasattr(result_pagto.data_pagamento, 'strftime')
                    else str(result_pagto.data_pagamento)
                )
                return (
                    f"SYSTEM_DATA: Relatório de {aluno_nome_real} (ID {aluno_id}):\n"
                    f"- Último Pagamento: {data_fmt}\n"
                    f"- Valor: R$ {result_pagto.valor}"
                )
            else:
                return f"SYSTEM_DATA: {aluno_nome_real} (ID {aluno_id}) não tem pagamentos cadastrados."

    except Exception as e:
        return f"SYSTEM_ERROR: {str(e)}"
