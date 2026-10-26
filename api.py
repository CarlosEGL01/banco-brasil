from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field, field_validator
from banco import Banco
from cliente import Cliente, Endereco
from excecoes import BancoError

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