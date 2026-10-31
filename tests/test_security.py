import os

# Configuração fictícia antes de importar a app
os.environ.update(
    GROQ_API_KEY="test",
    TWILIO_ACCOUNT_SID="ACtest",
    TWILIO_AUTH_TOKEN="token-de-teste",
    TWILIO_PHONE_NUMBER="whatsapp:+10000000000",
    PUBLIC_WEBHOOK_URL="https://example.test/whatsapp",
    ALLOWED_NUMBERS="whatsapp:+5581911112222",
    DATABASE_URL="sqlite://",
    PERSONAL_DB_URL="sqlite://",
)

from unittest.mock import patch  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402
from twilio.request_validator import RequestValidator  # noqa: E402

from app.core.security import mask_number  # noqa: E402
from app.main import app  # noqa: E402

URL = "https://example.test/whatsapp"
AUTHORIZED = "whatsapp:+5581911112222"


def _signed(form: dict) -> dict:
    return {"X-Twilio-Signature": RequestValidator("token-de-teste").compute_signature(URL, form)}


def test_rejeita_sem_assinatura():
    with TestClient(app) as client:
        r = client.post("/whatsapp", data={"Body": "oi", "From": AUTHORIZED})
    assert r.status_code == 403


def test_rejeita_assinatura_invalida():
    with TestClient(app) as client:
        r = client.post(
            "/whatsapp",
            data={"Body": "oi", "From": AUTHORIZED},
            headers={"X-Twilio-Signature": "forjada"},
        )
    assert r.status_code == 403


def test_ignora_numero_nao_autorizado():
    form = {"Body": "lista os alunos", "From": "whatsapp:+5511900000000"}
    with patch("app.main.get_groq_response") as ai, patch("app.main.twilio_client") as tw:
        with TestClient(app) as client:
            r = client.post("/whatsapp", data=form, headers=_signed(form))
    assert r.status_code == 200
    ai.assert_not_called()
    tw.messages.create.assert_not_called()


def test_responde_numero_autorizado():
    form = {"Body": "oi", "From": AUTHORIZED}
    with patch("app.main.get_groq_response", return_value="olá") as ai, patch("app.main.twilio_client") as tw:
        with TestClient(app) as client:
            r = client.post("/whatsapp", data=form, headers=_signed(form))
    assert r.status_code == 200
    ai.assert_called_once()
    tw.messages.create.assert_called_once()
    assert tw.messages.create.call_args.kwargs["body"] == "olá"


def test_falha_da_ia_envia_resposta_generica():
    form = {"Body": "oi", "From": AUTHORIZED}
    with patch("app.main.get_groq_response", side_effect=RuntimeError("detalhe interno do banco")), \
            patch("app.main.twilio_client") as tw:
        with TestClient(app) as client:
            client.post("/whatsapp", data=form, headers=_signed(form))
    body = tw.messages.create.call_args.kwargs["body"]
    assert "detalhe interno" not in body


def test_mask_number():
    assert mask_number("whatsapp:+5581999991234") == "whatsapp:+55*******1234"
