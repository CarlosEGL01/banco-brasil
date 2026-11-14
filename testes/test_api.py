import os
os.environ["BANCO_DB_PATH"] = "banco-testes.db"

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from excecoes import BancoError
from api import app
from banco import apagar_dados_sqlite



dados_cliente = {
    "nome": "Carlos Silva",
    "cpf": "12345678901",
    "phone": "48999999999",
    "endereco": {
        "rua": "Rua das Flores",
        "bairro": "Centro",
        "cidade": "Criciúma",
        "cep": "88800000"
    }
}

client = TestClient(app)

apagar_dados_sqlite() #Apagamos os dados antes de iniciar os testes

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


def test_cadastrar_cliente():
    resposta = client.post("/clientes", json=dados_cliente)
    
    assert resposta.status_code == 201
    assert resposta.json()["mensagem"] == "Cliente cadastrado com sucesso"

def test_cadastrar_cliente_mesmo_cpf():
    resposta = client.post("/clientes", json=dados_cliente)

    assert resposta.status_code == 409
    