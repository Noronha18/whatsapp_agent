# Agente de WhatsApp com IA para Personal Trainers

Agente conversacional no WhatsApp que responde perguntas do personal trainer consultando **dados reais** da base do [PTRoster](https://github.com/Noronha18/PTRoster), como a lista de alunos e o último pagamento de cada um. O modelo da Groq (Llama 3.3 70B) decide sozinho quando chamar uma ferramenta (*tool calling*) e redige a resposta a partir do resultado, sem inventar dados.

```
Personal: "A Ana já pagou este mês?"
Agente:   "O último pagamento da Ana foi em 05/10/2026, no valor de R$ 250,00."
```

---

## Como funciona

```
WhatsApp ──► Twilio ──► POST /whatsapp (FastAPI)
                          │ 1. valida assinatura X-Twilio-Signature
                          │ 2. confere número na allowlist
                          ▼
                     ai_service ──► Groq (Llama 3.3 70B, tool calling)
                          │              │
                          │              └─► tools_service ──► PostgreSQL do PTRoster (leitura)
                          │
                          ├─► histórico das últimas 5 mensagens por número (PostgreSQL próprio)
                          ▼
                     Twilio REST API ──► resposta no WhatsApp
```

1. A Twilio encaminha cada mensagem recebida para o webhook.
2. O webhook só aceita requisições **assinadas pela Twilio** e só atende números **autorizados**.
3. O agente monta o contexto com as últimas mensagens da conversa e chama a Groq com as ferramentas disponíveis.
4. Se o modelo pedir uma ferramenta, a consulta roda na base do PTRoster e o resultado volta ao modelo, que escreve a resposta final.
5. A resposta é enviada pela API REST da Twilio e salva no histórico.

### Ferramentas do modelo

| Tool | O que faz |
|---|---|
| `lista_alunos` | Lista os alunos cadastrados (limitado a 50) |
| `consultar_pagamento_aluno(nome_aluno)` | Busca o aluno por nome e retorna o último pagamento |

---

## Segurança

O agente expõe dados financeiros de pessoas reais, então o acesso é fechado por padrão:

- **Allowlist de números:** só os números em `ALLOWED_NUMBERS` recebem resposta. As mensagens de outros números são ignoradas em silêncio, sem chamar a IA nem revelar que o agente existe.
- **Assinatura da Twilio:** toda requisição ao webhook precisa de um `X-Twilio-Signature` válido, calculado com o Auth Token. Requisições forjadas recebem `403`.
- **Erros genéricos:** falhas de banco ou da IA são registradas no log do servidor. O usuário recebe só uma mensagem genérica, e nenhum detalhe interno chega ao modelo ou ao WhatsApp.
- **Logs sem dados pessoais:** os números aparecem mascarados (`whatsapp:+55*******1234`).
- **Banco do PTRoster somente leitura:** as consultas são parametrizadas, e a recomendação é conectar com um usuário sem permissão de escrita.
- **Prompt endurecido:** o modelo é instruído a ignorar pedidos para mudar as regras ou revelar o prompt.

---

## Stack

| Camada | Tecnologia |
|---|---|
| API | Python 3.12 · FastAPI · Pydantic Settings |
| IA | Groq API · Llama 3.3 70B Versatile (tool calling) |
| Mensageria | Twilio WhatsApp (Sandbox ou número aprovado) |
| Dados | PostgreSQL · SQLAlchemy 2 |
| Ambiente | uv · ngrok (túnel em desenvolvimento) |
| Testes | pytest · FastAPI TestClient |

---

## Estrutura

```
app/
├── main.py                       # Webhook /whatsapp e /health
├── core/
│   ├── config.py                 # Variáveis de ambiente (Pydantic Settings)
│   ├── database.py               # Engine e sessão do banco de conversas
│   └── security.py               # Assinatura Twilio, allowlist, máscara de número
├── models/conversations.py       # Tabela de histórico de mensagens
├── repositories/
│   └── conversation_repository.py
└── services/
    ├── ai_service.py             # Orquestração Groq + tool calling
    └── tools_service.py          # Consultas à base do PTRoster
tests/
└── test_security.py              # Assinatura, allowlist e falhas
init_db.py                        # Cria as tabelas do histórico
```

---

## Como rodar

**Requisitos:** Python 3.12+, [uv](https://docs.astral.sh/uv/), PostgreSQL, conta na [Groq](https://console.groq.com) e na [Twilio](https://www.twilio.com/) (o WhatsApp Sandbox serve para testes) e [ngrok](https://ngrok.com/).

```bash
uv sync
cp .env.example .env          # preencha as variáveis
uv run python init_db.py      # cria a tabela de conversas
uv run fastapi dev app/main.py --port 8000
```

Em outro terminal, exponha o servidor:

```bash
ngrok http 8000
```

No console da Twilio, em *WhatsApp Sandbox → When a message comes in*, cadastre `https://<seu-ngrok>/whatsapp` (POST). Use **exatamente a mesma URL** em `PUBLIC_WEBHOOK_URL`, porque a assinatura é calculada sobre ela.

### Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `GROQ_API_KEY` | Chave da Groq |
| `GROQ_MODEL` | Modelo (padrão `llama-3.3-70b-versatile`) |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | Credenciais da Twilio |
| `TWILIO_PHONE_NUMBER` | Número remetente, ex.: `whatsapp:+14155238886` |
| `PUBLIC_WEBHOOK_URL` | URL pública do webhook, usada na validação da assinatura |
| `VALIDATE_TWILIO_SIGNATURE` | `true` por padrão. Desligue só em testes locais |
| `ALLOWED_NUMBERS` | Números autorizados, separados por vírgula (`whatsapp:+55...`) |
| `DATABASE_URL` | PostgreSQL do histórico de conversas |
| `PERSONAL_DB_URL` | PostgreSQL do PTRoster (use um usuário somente leitura) |

### Testes

```bash
uv run pytest
```

Os testes cobrem assinatura ausente ou inválida, número não autorizado, fluxo autorizado e a resposta genérica em caso de falha. Usam SQLite em memória e mocks da Groq e da Twilio, sem chamadas externas.

---

## Próximos passos

- Fila assíncrona para o processamento (a Twilio espera resposta do webhook em até 15 s)
- Mais ferramentas: frequência do aluno e saldo de aulas de pacote
- Deploy com HTTPS fixo no lugar do ngrok

---

## Autor

**Emmanuel Noronha**, desenvolvedor Full-Stack.
