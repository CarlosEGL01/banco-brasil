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
            "rua": self.rua,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "cep": self.cep
        }
    @classmethod
    def de_dict(cls,dados):
        return cls(
            dados["rua"],
            dados["bairro"],
            dados["cidade"],
            dados["cep"]

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
            "nome": self.nome,
            "cpf": self.cpf,
            "phone": self.phone,
            "endereco": self.endereco.para_dict()
        }
    
    @classmethod
    def de_dict(cls,dados):
        endereco = Endereco.de_dict(dados["endereco"])
        return cls(
            dados["nome"],
            dados["cpf"],
            dados["phone"],
            endereco
        )


