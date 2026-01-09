# test_db.py (VERSÃO COMPLETA)
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("PERSONAL_DB_URL")
print(f"🔍 DB_URL: {DB_URL}")

engine = create_engine(DB_URL)

with engine.connect() as conn:
    print("✅ Conexão OK")

    # CONTAGEM GERAL
    print("\n📊 RESUMO:")
    alunos = conn.execute(text("SELECT COUNT(*) as total FROM alunos")).fetchone()
    print(f"Alunos totais: {alunos.total}")

    pagtos = conn.execute(text("SELECT COUNT(*) as total FROM pagamentos")).fetchone()
    print(f"Pagamentos totais: {pagtos.total}")

    # ALUNOS ESPECÍFICOS
    print("\n👩‍🦰 ALUNOS:")
    alunos_nomes = conn.execute(
        text("SELECT nome FROM alunos WHERE nome ILIKE '%carine%' OR nome ILIKE '%adriana%'")).fetchall()
    for aluno in alunos_nomes:
        print(f"  - {aluno.nome}")

    # PAGAMENTOS DE CARINE (se existir)
    print("\n💰 PAGAMENTOS CARINE:")
    carine = conn.execute(text("""
                               SELECT a.nome, p.data_pagamento, p.valor
                               FROM alunos a
                                        LEFT JOIN pagamentos p ON a.id = p.aluno_id
                               WHERE a.nome ILIKE '%carine%'
                               """)).fetchall()
    for row in carine:
        print(f"  - {row.nome}: {row.data_pagamento}, R${row.valor}")
