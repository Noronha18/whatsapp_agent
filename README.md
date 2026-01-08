# 🤖 Agente WhatsApp com IA (FastAPI + Groq)

Este projeto é um **Agente Conversacional** que atende usuários via WhatsApp utilizando a API da **Twilio** para mensageria e a **Groq (Llama 3)** para inteligência artificial ultra-rápida.

O projeto foi construído seguindo princípios de **Clean Architecture**, visando escalabilidade e desacoplamento entre a camada de API e os serviços de IA.

## 🚀 Tech Stack

- **Linguagem:** Python 3.12+
- **Framework Web:** FastAPI
- **Gerenciador de Pacotes:** uv (Astral)
- **IA / LLM:** Groq API (Llama-3.3-70b-versatile)
- **Mensageria:** Twilio (WhatsApp Sandbox)
- **Infra Local:** Ngrok (Túnel HTTP)
- **Validação:** Pydantic V2

## 🏗️ Arquitetura

O projeto segue uma estrutura modular para facilitar manutenção:

```text
whatsapp_agent/
├── app/
│   ├── core/         # Configurações e Variáveis de Ambiente (Pydantic)
│   ├── routers/      # Endpoints HTTP (Webhook Controller)
│   ├── services/     # Lógica de Negócio e Integrações Externas (Groq/OpenAI)
│   └── main.py       # Entrypoint da aplicação
├── .env              # (Ignorado no Git) Segredos e Chaves
├── pyproject.toml    # Dependências do uv
└── uv.lock
