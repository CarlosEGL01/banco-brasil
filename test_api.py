from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_inicio():
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "mensagem": "Bem-vindo à API do Banco Brasil"
    }


def test_status():
    resposta = client.get("/status")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "operacional"