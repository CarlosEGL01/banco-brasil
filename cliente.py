
import sqlite3
conexao = sqlite3.connect("banco.db")
conexao.execute("PRAGMA foreign_key = ON")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cliente (
    numero INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf INTEGER UNIQUE NOT NULL,
    phone INTEGER NOT NULL
)
""")
conexao.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS endereco (
    numero INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_numero INTEGER UNIQUE NOT NULL,
    rua TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    cep TEXT NOT NULL,

    FOREIGN KEY (cliente_numero) REFERENCES cliente(numero)
)
""")
conexao.commit()



class Endereco:
    def __init__(self, rua, bairro, cidade, cep):
        self.rua = rua
        self.bairro = bairro
        self.cidade = cidade 
        self.cep = cep
    def __str__(self):
        return f"Rua: {self.rua} - Bairro: {self.bairro} - Cidade: {self.cidade} - CEP: {self.cep}"
    
    def para_dict(self):
        return{
            "Rua": self.rua,
            "Bairro": self.bairro,
            "Cidade": self.cidade,
            "CEP": self.cep
        }
    @classmethod
    def de_dict(cls,dados):
        return cls(
            dados["Rua"],
            dados["Bairro"],
            dados["Cidade"],
            dados["CEP"]

        )
    
class Cliente: 
    def __init__(self, nome, cpf, phone, endereco):
        self.nome = nome
        self.cpf = cpf
        self.phone = phone
        self.endereco = endereco

    def __str__(self):
        return f"{self.nome} -  CPF: {self.cpf} - Telefone: {self.phone} - Endereço: {self.endereco}"
    
    def para_dict(self):
        return{
            "Nome": self.nome,
            "CPF": self.cpf,
            "Telefone": self.phone,
            "Endereco": self.endereco.para_dict()
        }
    
    @classmethod
    def de_dict(cls,dados):
        endereco = Endereco.de_dict(dados["Endereco"])
        return cls(
            dados["Nome"],
            dados["CPF"],
            dados["Telefone"],
            endereco
        )

