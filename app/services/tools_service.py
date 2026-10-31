"""Ferramentas que o modelo pode chamar. Acesso somente leitura à base do PTRoster."""
import logging
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text

from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_ALUNOS = 50
TOOL_ERROR = "SYSTEM_ERROR: Não foi possível consultar os dados agora."


@lru_cache
def _engine() -> Engine:
    # Criado sob demanda: importar o módulo não abre conexão com o banco
    return create_engine(settings.PERSONAL_DB_URL, pool_pre_ping=True)


def lista_alunos() -> str:
    try:
        with _engine().connect() as conn:
            rows = conn.execute(
                text("SELECT id, nome FROM alunos ORDER BY nome LIMIT :lim"), {"lim": MAX_ALUNOS}
            ).fetchall()
    except Exception:
        logger.exception("Erro em lista_alunos")
        return TOOL_ERROR

    if not rows:
        return "SYSTEM_DATA: Nenhum aluno encontrado."
    lista = "\n".join(f"- {r.nome} (ID: {r.id})" for r in rows)
    return f"SYSTEM_DATA: Lista de alunos:\n{lista}"


def consultar_pagamento_aluno(nome_aluno: str) -> str:
    try:
        with _engine().connect() as conn:
            aluno = conn.execute(
                text("SELECT id, nome FROM alunos WHERE nome ILIKE :nome ORDER BY nome LIMIT 1"),
                {"nome": f"%{nome_aluno}%"},
            ).fetchone()
            if not aluno:
                return f"SYSTEM_DATA: Não encontrei aluno com nome '{nome_aluno}'."

            pagamento = conn.execute(
                text(
                    "SELECT data_pagamento, valor FROM pagamentos "
                    "WHERE aluno_id = :aid ORDER BY data_pagamento DESC LIMIT 1"
                ),
                {"aid": aluno.id},
            ).fetchone()
    except Exception:
        logger.exception("Erro em consultar_pagamento_aluno")
        return TOOL_ERROR

    if not pagamento:
        return f"SYSTEM_DATA: {aluno.nome} não tem pagamentos registrados."
    return (
        f"SYSTEM_DATA: Último pagamento de {aluno.nome}:\n"
        f"- Data: {pagamento.data_pagamento.strftime('%d/%m/%Y')}\n"
        f"- Valor: R$ {pagamento.valor:.2f}"
    )
