from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field, field_validator
from banco import Banco
from cliente import Cliente, Endereco
from excecoes import BancoError, ClienteNaoEncontradoError, MesmaContaError, ContaEncerradaError,ContaNaoEncontradaError, ContaNaoEncerradaError, SaldoInsuficienteError 

app = FastAPI(title="Banco Do Brasil API 0.2")


@app.get("/")
def inicio():
    return {"mensagem": "Bem-vindo à API do Banco Brasil"}


@app.get("/status")
def verificar_status():
    return {
        "aplicacao": "Banco Brasil",
        "status": "operacional"
    }

class EnderecoEntrada(BaseModel):
    rua: str = Field(min_length=1, max_length=100)
    bairro: str = Field(min_length=1, max_length=100)
    cidade: str = Field(min_length=1, max_length=100)
    cep: str = Field(min_length=8, max_length=9)


class ClienteEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    cpf: str = Field(min_length=11, max_length=14)
    phone: str = Field(min_length=8, max_length=20)
    endereco: EnderecoEntrada

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("O nome não pode estar vazio.")

        return valor

banco = Banco("Banco Brasil")
@app.post("/clientes", status_code=201)
def cadastrar_cliente(dados: ClienteEntrada):
    endereco = Endereco(
        dados.endereco.rua,
        dados.endereco.bairro,
        dados.endereco.cidade,
        dados.endereco.cep
    )

    cliente = Cliente(
        dados.nome,
        dados.cpf,
        dados.phone,
        endereco
    )

    try:
        cliente_cadastrado = banco.cadastrar_cliente(cliente)
    except BancoError as erro:
        raise HTTPException(status_code=409, detail=str(erro))

    return {
        "mensagem": "Cliente cadastrado com sucesso",
        "cliente": cliente_cadastrado.para_dict()
    }

@app.get("/clientes/{cpf}")
def consultar_cliente(cpf: str):
    cliente = banco.buscar_cliente(cpf)

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado."
        )

    return cliente.para_dict()



@app.get("/clientes/{cpf}/contas")
def consultar_contas_cliente(cpf: str):
    cliente = banco.buscar_cliente(cpf)

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado."
        )

    contas = banco.buscar_contas_cpf(cpf)

    return {
        "cliente": cliente.nome,
        "total_contas": len(contas),
        "contas": [
            conta.para_dict()
            for conta in contas
        ]
    }




@app.post("/clientes/{cpf}/cadastrar-conta",status_code=201)
def cadastrar_conta(cpf: str, tipo: str):
    try:
        cliente = banco.buscar_cliente(cpf)
        conta = banco.abrir_conta(cliente, tipo)
    except ClienteNaoEncontradoError as erro:
        raise HTTPException(status_code=404, detail=str(erro))
    except MesmaContaError as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    except BancoError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return {
        "mensagem": "Conta criada com sucesso",
        "cliente": conta.para_dict()
    }

    

@app.get("/conta/{numero}")
def consultar_conta(numero: int):
    try:
        conta = banco.buscar_conta(numero)

    except ContaNaoEncontradaError as e:
        raise HTTPException(status_code= 404, detail=str(e))
    except BancoError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "mensagem": f"Bem-vindo a conta {numero}",
        "conta": conta.para_dict()
    }



@app.post("/conta/depositar", status_code=201)
def depositar_conta(conta: int, dinheiro: float):
    try:
        conta = banco.buscar_conta(conta)
        saldo_anterior = conta.saldo
        conta_atual = conta.depositar(dinheiro)

    except ContaNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ContaEncerradaError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BancoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "mensagem: ": " Deposito com sucesso.",
        "saldo anterior": saldo_anterior,
        "saldo atual: ": conta_atual.saldo,
        "conta": conta_atual.para_dict()
    }
@app.post("/conta/sacar", status_code=201)
def sacar_conta(conta: int, dinheiro: float):
    try:
        conta = banco.buscar_conta(conta)
        saldo_anterior = conta.saldo
        conta_atual = conta.sacar(dinheiro)
    except ContaNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ContaEncerradaError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SaldoInsuficienteError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BancoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "mensagem: ": " Saque com sucesso.",
        "saldo anterior": saldo_anterior,
        "saldo atual: ": conta_atual.saldo,
        "conta": conta_atual.para_dict()
    }


@app.post("/banco/transferencia", status_code=201)
def transferencia(num_origem: int, num_destino: int, valor: float):
    try:
        banco = Banco("Banco Do Brasil")
        banco.transferencia(num_origem, num_destino, valor)

        conta_origem = banco.buscar_conta(num_origem)
        conta_destino = banco.buscar_conta(num_destino)
        

    except ContaNaoEncontradaError as e:
       raise HTTPException(status_code=404, detail=str(e))
    except ContaEncerradaError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MesmaContaError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except SaldoInsuficienteError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BancoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "mensagem: ": " Transferencia com sucesso.",
        "valor da transacao: ": valor,
        "Historico Origem": conta_origem.historico[-1],
        "Historico Destino: ": conta_destino.historico[-1]
    }