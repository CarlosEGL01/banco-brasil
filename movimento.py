import locale
import sqlite3
conexao = sqlite3.connect("banco.db", check_same_thread=False)
conexao.execute("PRAGMA foreign_key = ON")
cursor = conexao.cursor()

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
          return super().__str__() + f" \nConta Origem: {self.origem} \nConta_Destino: {self.destino} \nValor: R${locale.format_string("%.2f", self.valor, grouping=True)}"
     def para_dict(self):
          dic_pai = super().para_dict()
          dic_filho = {"Conta_Origem": self.origem, "Conta_Destino": self.destino, "Valor": self.valor}
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

     def criar_movimento(operacao):
          if operacao == "Transferencia Enviada" or operacao == "Transferencia Recebida":
               operacao = "Transferencia"
          
          fabrica = {
              "Deposito": Movimento_Deposito,
              "Transferencia": Movimento_Transferencia,
              "Saque": Movimento_Saque
          }
          class_movimento = fabrica.get(operacao, Movimento)

          return class_movimento
     
     def restaurar_historico(numero_conta):
          #CONSULTANDO HISTORICO: DEPOSITO / SAQUE / GERAL.
          try:
               #CONSULTANDO HISTORICO: DEPOSITO / SAQUE / GERAL.
               cursor.execute("SELECT * FROM historico WHERE numero_conta = ?" , (numero_conta,))
               movimentos = cursor.fetchall()
               movimentos_objetos = []

               #CONSULTANDO HISTORICO TRANSFERENCIA 
               cursor.execute("SELECT * FROM historico_transferencia WHERE numero_conta = ?" , (numero_conta,))
               movimento_trans = cursor.fetchall()          
          except sqlite3.Error as e:
               print(e)
          if len(movimentos) != 0:
               for movimento in movimentos:
                    tipo = movimento[2]
                    status = movimento[3]
                    data = movimento[4]
                    valor = movimento [5]
                    classe = Fabrica_de_Movimento.criar_movimento(tipo)
               
                    movimento_n = classe(tipo,status,data, valor)
                    movimentos_objetos.append(movimento_n)
          else:
               return movimentos_objetos
          if len(movimento_trans) != 0:
               for movimento in movimento_trans:
                    tipo = movimento[2]
                    status = movimento[3]
                    data = movimento[4]
                    valor = movimento [6]
                    
                    if tipo == "Transferencia Enviada":
                         origem = movimento[1]
                         destino = movimento[5]
                         classe = Fabrica_de_Movimento.criar_movimento(tipo)
                         movimento_n = classe(tipo, status, data, origem, destino,valor)
                         movimentos_objetos.append(movimento_n)
                    elif tipo == "Transferencia Recebida":
                         classe = Fabrica_de_Movimento.criar_movimento(tipo)
                         origem = movimento[5]
                         destino = movimento[1]
                         movimento_n = classe(tipo, status, data, origem, destino,valor)
                         movimentos_objetos.append(movimento_n)

          else:
               return movimentos_objetos

          return movimentos_objetos

if __name__ == "__main__":
    lista = Fabrica_de_Movimento.restaurar_historico(2)

    