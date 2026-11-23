import os
os.environ["BANCO_DB_PATH"] = "banco-testes.db"

from fastapi.testclient import TestClient
from api import app
from banco import apagar_dados_sqlite
import pytest

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

#-----------------------Testes de cadastro-------------------------------------#
def test_cadastrar_cliente():
    resposta = client.post("/clientes", json=dados_cliente)
    
    assert resposta.status_code == 201
    assert resposta.json()["mensagem"] == "Cliente cadastrado com sucesso"

def test_cadastrar_cliente_mesmo_cpf():
    resposta = client.post("/clientes", json=dados_cliente)

    assert resposta.status_code == 409


def test_cadastrar_cliente_nome_curto():
    dados_invalidos = dados_cliente.copy()
    dados_invalidos["nome"] = "C"
    resposta = client.post("/clientes", json=dados_invalidos)

    assert resposta.status_code == 422

def test_cadastrar_cliente_endereco_vazio():
    dados_invalidos = dados_cliente.copy()
    dados_invalidos["endereco"] = ""

    resposta = client.post("/clientes", json=dados_invalidos)

    assert resposta.status_code == 422

def test_cadastrar_cliente_endereco_sem_endereco():
    dados_invalidos = dados_cliente.copy()
    del dados_invalidos["endereco"]
    
    resposta = client.post("/clientes", json=dados_invalidos)
    
    assert resposta.status_code == 422

def test_cadastrar_cliente_endereco_sem_cidade():
    dados_invalidos = dados_cliente.copy()
    
    del dados_invalidos["endereco"]["cidade"]
    
    resposta = client.post("/clientes", json=dados_invalidos)
    
    assert resposta.status_code == 422


#------------Testes consultar cliente--------------------
def test_consultar_cliente():
    
    resposta = client.get("/clientes/12345678901")
    assert resposta.status_code == 200
    assert resposta.json()["cpf"] == int(dados_cliente["cpf"])


def test_consultar_cliente_inexistente():
    resposta = client.get("/clientes/11407147242")
    assert resposta.status_code == 404


#------------Testes cadastrar contas----------------------
dados = {
        "cpf": "12345678901",
        "tipo": "Conta_Corrente"
    } #Cliente já existente
def test_cadastrar_conta():
    
    resposta = client.post("/clientes/12345678901/cadastrar-conta", params=dados)
    assert resposta.status_code == 201
    assert resposta.json()["mensagem"] == "Conta criada com sucesso"

def test_cadastrar_conta_cliente_inexistente():
    dados["cpf"] = "111111111111" #Cliente inexistente
    
    resposta = client.post("/clientes/111111111111/cadastrar-conta", params=dados)
    assert resposta.status_code == 404
def test_cadastrar_mesma_conta():

    resposta = client.post("/clientes/12345678901/cadastrar-conta", params=dados)
    assert resposta.status_code == 409

def test_cadastrar_conta_inexistente():

    dados["tipo"] = "Conta_Universal" #CONTA INEXISTENTE
    resposta = client.post("/clientes/12345678901/cadastrar-conta", params=dados)
    assert resposta.status_code == 400
    
#------------Testes consultar CONTAS cliente--------------
def test_consultar_contas_cliente():

    resposta = client.get("/clientes/12345678901/contas")
    
    assert resposta.status_code == 200
    assert resposta.json()["cliente"] == dados_cliente["nome"]
    assert resposta.json()["total_contas"] ==  1

def test_consultar_contas_cliente_inexistente():
    resposta = client.get("/clientes/11111111111/contas")

    assert resposta.status_code == 404


#------------Testes Consultar CONTA-------------------
def test_consultar_conta():
    numero = 1
    resposta = client.get("/conta/1")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == f"Bem-vindo a conta {numero}" 

def test_conta_nao_encontrada():

    resposta = client.get("/conta/2")

    assert resposta.status_code == 404

#-----------TESTES Consultar historico---------------------

def test_consultar_historico():
    numero = 1
    resposta = client.get("/conta/1/historico")
    
    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == f"Bem-vindo a conta {numero}"
    assert resposta.json()["total_movimentacoes"] == 0

#------TESTES Depositar POST --------

valores = {
    "numero": "1",
    "dinheiro": "100"
}
def test_depositar_dinheiro_conta():
    
    resposta = client.post("/conta/1/depositar", params=valores)

    assert resposta.status_code == 201
    assert resposta.json()["mensagem"] == " Deposito com sucesso."

def test_depositar_conta_nao_encontrada():
    resposta = client.post("/conta/99/depositar", params=valores)

    assert resposta.status_code == 404

#Utilizar parametrize
@pytest.mark.parametrize("valores_invalidos", ["", "Oi", "1as", "-1"])
def test_depositar_valor_invalido(valores_invalidos):
    
    resposta = client.post("/conta/1/depositar", params={"dinheiro": valores_invalidos})

    assert resposta.status_code == 422


#------------------TESTES Encerrar Conta PATH-----------------------

def test_cadastrar_conta_(): #Cadastramos esta conta para demonstrações de encerramento #CONTA 2
    dados["tipo"] = "Conta_Universitaria"
    resposta = client.post("/clientes/12345678901/cadastrar-conta", params=dados)
    assert resposta.status_code == 201
    assert resposta.json()["mensagem"] == "Conta criada com sucesso"

def test_encerrar_conta_com_dinheiro():
    resposta = client.patch("/banco/encerrar-conta/1") #Conta 1 possui dinheiro

    assert resposta.status_code == 409

def test_encerrar_conta():
    resposta = client.patch("/banco/encerrar-conta/2")
    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "Conta encerrada com sucesso"

def test_encerrar_conta_nao_encontrada():

    resposta = client.patch("/banco/encerrar-conta/3")

    assert resposta.status_code == 404

def test_encerrar_conta_ja_encerrada():

    resposta = client.patch("/banco/encerrar-conta/2") #Encerramos a mesma conta

    assert resposta.status_code == 409
#------- TESTES DE DEPOSITAR E TRANSFERIR COM CONTA ENCERRADA ----------
def test_depositar_conta_encerrada(): #Test de deposito colocado aqui, porque se colocasse cima não ia rolar, nao tinha uma conta encerrada
    resposta = client.post("/conta/2/depositar", params=valores)

    assert resposta.status_code == 409


def test_transferencia_conta_encerrada():

    resposta = client.post("/banco/1/2/transferencia", params={"valor":15}) #Conta dois está encerrada

    assert resposta.status_code == 409

#----------TESTES Sacar dinheiro POST -------------------
def test_sacar_dinherio():

    valores["dinheiro"] = 10

    resposta = client.post("/conta/1/sacar", params=valores)

    assert resposta.status_code == 201
    assert resposta.json()["mensagem"] == " Saque com sucesso."

def test_sacar_conta_nao_encontrada():

    resposta = client.post("/conta/99/sacar", params=valores)

    assert resposta.status_code == 404

def test_sacar_conta_encerrada():   
    valores["numero"] = 2

    resposta = client.post("/conta/2/sacar", params=valores)

    assert resposta.status_code == 409
@pytest.mark.parametrize("valor_invalido", ["", "Oi", "1as", "-1"])
def test_sacar_dinheiro_valores_invalidos(valor_invalido):
    
    resposta = client.post("/conta/1/sacar", params={"dinheiro": valor_invalido})

    assert resposta.status_code == 422

def test_sacar_saldo_insuficiente():
    valores["dinheiro"] = 200

    resposta = client.post("/conta/1/sacar", params=valores)

    assert resposta.status_code == 409

    
#--------- TESTES DE REABERTURA path-------------------

def test_reabertura_conta():
    resposta = client.patch("/banco/reabertura-conta/2")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"]  == "Re-abertura de conta com sucesso"

def test_reabertura_conta_nao_encontrada():
    resposta = client.patch("/banco/reabertura-conta/99")

    assert resposta.status_code == 404

def test_reabertura_conta_ja_reaberta_ou_aberta():
    resposta = client.patch("/banco/reabertura-conta/2")

    assert resposta.status_code == 409


#--------- TESTES DE TRANSFERENCIA ------------------

def test_transferencia():
    
    resposta = client.post("/banco/1/2/transferencia", params={"valor":15})

    assert resposta.status_code == 201

    assert resposta.json()["mensagem"] == " Transferencia com sucesso."
    assert resposta.json()["valor da transacao"] == 15


@pytest.mark.parametrize("conta_o, conta_d", [("99","1"), ("2","99")])
def test_transferencia_conta_nao_encontrada(conta_o,conta_d):

    resposta = client.post(f"/banco/{conta_o}/{conta_d}/transferencia", params={"valor": 15} )

    assert resposta.status_code == 404

@pytest.mark.parametrize("valor_invalido", ["", "Oi", "1as", "-1"])
def test_transferencia_valor_invalido(valor_invalido):

    resposta = client.post("/banco/1/2/transferencia", params=valor_invalido)

    assert resposta.status_code == 422

def test_transferencia_mesma_conta():
    resposta = client.post("/banco/1/1/transferencia", params={"valor":15})

    assert resposta.status_code == 409

def test_transferencia_saldo_insuficiente():

    resposta = client.post("/banco/1/2/transferencia", params={"valor":500})

    assert resposta.status_code == 409