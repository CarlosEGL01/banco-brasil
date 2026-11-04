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



list = []

print(len(list))