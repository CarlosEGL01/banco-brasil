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


     def restaurar_historico_transferencia(numero_conta):
          from banco import Banco
          
          #CONSULTANDO HISTORICO TRANSFERENCIA
          try:
               cursor.execute("SELECT * FROM historico_transferencia WHERE numero_conta = ?" , (numero_conta,))
               lista_movimentos_historico = cursor.fetchall()
               banco = Banco("Banco Do Brasil")          
               lista_movimentos_objetos = []
          except sqlite3.Error as e:
               print("Error")
               print(e)
          else:
               print("Sucesso")
          finally:
               
               print("Finalizado")

          for movimento in lista_movimentos_historico:
               tipo = movimento[2]
               if tipo == "Transferencia Enviada":
                    classe = Fabrica_de_Movimento.criar_movimento(tipo)
                    origem = movimento[1]
                    destino = movimento[5]
                    movimento_n = classe(tipo, movimento[3], movimento[4], origem, destino,movimento[6])
                    lista_movimentos_objetos.append(movimento_n)
               elif tipo == "Transferencia Recebida":
                    classe = Fabrica_de_Movimento.criar_movimento(tipo)
                    origem = movimento[5]
                    destino = movimento[1]
                    movimento_n = classe(tipo, movimento[3], movimento[4], origem, destino,movimento[6])
                    lista_movimentos_objetos.append(movimento_n)

          return lista_movimentos_objetos
     
     def restaurar_historico(numero_conta):
          conexao = sqlite3.connect("banco.db", check_same_thread=False)
          conexao.execute("PRAGMA foreign_key = ON")
          cursor = conexao.cursor()
          #CONSULTANDO HISTORICO
          cursor.execute("SELECT * FROM historico WHERE numero_conta = ?" , (numero_conta,))
          lista_movimentos = cursor.fetchall()
          lista_movimentos_objetos = []
          
          for movimento in lista_movimentos:
               
               classe = Fabrica_de_Movimento.criar_movimento(movimento[2])
          
               movimento_n = classe(movimento[2],movimento[3],movimento[4], movimento[5])
               lista_movimentos_objetos.append(movimento_n)

          lista_movimentos_objetos_trans = Fabrica_de_Movimento.restaurar_historico_transferencia(numero_conta)

          return lista_movimentos_objetos + lista_movimentos_objetos_trans



          
          

if __name__ == "__main__":
    lista = Fabrica_de_Movimento.restaurar_historico(2)

    