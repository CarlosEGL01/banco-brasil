import locale

# Define a configuração para o padrão do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
class Movimento:
     def __init__(self,tipo,status,data):
          self.tipo = tipo
          self.status = status
          self.data = data

     def __str__(self):
          return f"{self.data} \n{self.tipo} \nStatus: {self.status} "
     
     def para_dict(self):
          return{
               "Tipo": self.tipo,
               "Status": self.status,
               "Data": self.data
          }
     @classmethod
     def de_dict(cls,dados):
          return cls(
               dados["Tipo"],
               dados["Status"],
               dados["Data"]
          )

class Movimento_Deposito(Movimento):
     def __init__(self, tipo, status, data, valor):
          super().__init__(tipo, status, data)
          self.valor = valor
     
     def __str__(self):
          return super().__str__() + f" \nValor: R$ +{locale.format_string("%.2f", self.valor, grouping=True)}"
     
     def para_dict(self):
          dic_pai = super().para_dict()
          dic_filho = {"Valor": self.valor}
          novo_dic = dic_pai | dic_filho
          return novo_dic
     
     @classmethod
     def de_dict(cls, dados):
          return cls(dados["Tipo"], dados["Status"], dados["Data"], dados["Valor"])
     
class Movimento_Transferencia(Movimento):
     def __init__(self, tipo, status, data,origem,destino,valor):
          super().__init__(tipo, status, data)
          self.origem = origem
          self.destino = destino
          self.valor = valor
     def __str__(self):
          return super().__str__() + f" \nConta Origem: {self.origem.numero} \nConta_Destino: {self.destino.numero} \nValor: R${locale.format_string("%.2f", self.valor, grouping=True)}"
     def para_dict(self):
          dic_pai = super().para_dict()
          dic_filho = {"Conta_Origem": self.origem.numero, "Conta_Destino": self.destino.numero, "Valor": self.valor}
          novo_dic = dic_pai | dic_filho
          return novo_dic
     @classmethod
     def de_dict(cls,dados):
          return cls(
               dados["Tipo"],
               dados["Status"],
               dados["Data"],
               dados["Conta_Origem"],
               dados["Conta_Destino"],
               dados["Valor"]
          )

class Movimento_Saque(Movimento):
     def __init__(self, tipo, status, data, valor):
          super().__init__(tipo, status, data)
          self.valor = valor
     def __str__(self):
          return super().__str__() + f" \nValor: R$ -{locale.format_string("%.2f", self.valor, grouping=True)}"
     
     def para_dict(self):
          dic_pai = super().para_dict()
          dic_filho = {"Valor": self.valor}
          novo_dic = dic_pai | dic_filho
          return novo_dic
     
     @classmethod
     def de_dict(cls, dados):
          return cls(dados["Tipo"], dados["Status"], dados["Data"], dados["Valor"])

     

class Fabrica_de_Movimento():
     def resturar_movimento(dados):
          fabrica = {
               "Deposito": Movimento_Deposito,
               "Transferencia": Movimento_Transferencia,
               "Saque": Movimento_Saque
          }

          class_movimento = fabrica.get(dados["Tipo"], Movimento)

          movimento_novo = class_movimento.de_dict(dados)

          return movimento_novo

     

          

