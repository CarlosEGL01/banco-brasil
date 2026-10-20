from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

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

class ClienteEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    cpf: str

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("O nome não pode estar vazio.")

        return valor


@app.post("/clientes")
def cadastrar_cliente(cliente: ClienteEntrada):
    return {
        "mensagem": "Dados recebidos com sucesso",
        "cliente": cliente.model_dump()
    }

