from abc import ABC, abstractmethod
from movimento import Movimento, Movimento_Deposito, Movimento_Saque, Movimento_Transferencia
from excecoes import SaldoInsuficienteError, ContaEncerradaError, BancoError, CreditoInsuficienteError, ContaNaoEncerradaError 
import locale

# Define a configuração para o padrão do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
import sqlite3
conexao = sqlite3.connect("banco.db")
conexao.execute("PRAGMA foreign_key = ON")
cursor = conexao.cursor()

data_atual = "07/07/2026"
class Conta(ABC):
     def __init__(self,cliente, numero):
          self.cliente = cliente
          self.tipo = self.__class__.__name__
          self.numero = numero
          self.__saldo = 0
          self.__historico = []
          self.estado = "Ativa"

     def __str__(self):
          return f"Titular da conta: {self.cliente} - Tipo de conta: {self.tipo} - Numero de Conta: {self.numero} - Saldo: {self.saldo} - Historico: {self.historico} -Estado: {self.estado}"
     
     def para_dict(self):
          return{
               "Cliente": self.cliente.cpf,
               "Tipo": self.tipo,
               "Numero": self.numero,
               "Saldo": self.__saldo,
               "Historico": [movimento.para_dict() for movimento in self.__historico],
               "Estado": self.estado

          }
     
     @classmethod
     def de_dict(cls,dados):
          return cls(
               dados["Cliente"],
               dados["Numero"],
          )
     
     
     @property
     def saldo(self):
          if self.estado != "Ativa":
               return None
          return self.__saldo
     @saldo.setter
     def saldo(self,valor):
          self.__saldo = valor
               
     @property
     def historico(self):
          if self.estado != "Ativa":
               return None
          return self.__historico.copy()
     
     def depositar(self,valor):
          if self.estado != "Ativa":
               raise ContaEncerradaError("Não pode fazer esse movimento. CONTA ENCERRADA!")
          
          if isinstance(valor, str):
               raise ValueError("Digite um número")
          
          if valor <= 0:
               raise ValueError("Digite um numero válido")
          
          elif valor > 0:
               total = self.__saldo + valor
               self.__saldo += valor
               novo_movimento = Movimento_Deposito("Deposito","Sucesso",data_atual, valor)
               self.registrar_movimento(novo_movimento) 

               cursor.execute("""
                    UPDATE conta
                    SET saldo = ?
                    Where numero = ?
               """, (total, self.numero,))

               cursor.execute("""
                    INSERT INTO historico(numero_conta, operacao,status,data,valor)
                    VALUES(?,"Deposito", "Sucesso", ?, ?)
               """, (self.numero,data_atual,valor,))
               conexao.commit()
               return True
          

     def sacar(self,valor): #APLICAR O TRATAMENTO DE ERRO
          if self.estado != "Ativa":
               raise ContaEncerradaError("Não pode fazer esse movimento. CONTA ENCERRADA!")
          if valor <= 0 or isinstance(valor, str):
               raise ValueError("Número Inválido")
          if valor > self.__saldo: # 200 > 100 
               raise SaldoInsuficienteError("Não tem saldo para tirar esse valor")
          if valor == self.__saldo: ## É para vaziar conta e poder encerrar
               total = valor
          else:
               total = self.calcular_tarifa(valor) # Continua aplicando tarifa
          
          if total <= self.__saldo:  #PRECISA TESTAR
               total_final = self.__saldo - total
               self.__saldo -= total
               novo_movimento = Movimento_Saque("Saque","Sucesso",data_atual, total_final) 
               self.registrar_movimento(novo_movimento)
               #Guardando operação
               cursor.execute("UPDATE conta SET saldo = ? WHERE numero = ?", (total_final, self.numero))
               #HISTORICO AO SQL
               cursor.execute("""
                    INSERT INTO historico(numero_conta,operacao,status,data,valor)
                    VALUES(?,"Saque","Sucesso",?,?)
               """, (self.numero, data_atual, total,))
               conexao.commit()
               return True
          
          return None

     def consultar_historico(self,tipo=""):
          if tipo == "":
               cursor.execute("SELECT * FROM historico WHERE numero_conta = ?", (self.numero,))
               resultado_movimentos = cursor.fetchall()
               return resultado_movimentos

    
          
          cursor.execute("""
          SELECT * FROM historico
          WHERE numero_conta = ? AND operacao = ?
          """, (self.numero, tipo,))

          resultado_movimentos = cursor.fetchall()

          return resultado_movimentos

     
     def saldo_disponivel(self):
          return self.saldo #Num X

     def informacoes(self):
          cursor.execute("""
               SELECT 
               conta.numero,
               cliente.nome,
               cliente.cpf,
               conta.saldo,
               conta.tipo,
               conta.estado
               FROM conta 
               JOIN cliente 
                    ON conta.cliente_numero = cliente.numero
               WHERE conta.numero = ?
          """, (self.numero, ))

          return cursor.fetchone()

     @abstractmethod
     def calcular_tarifa(self,valor):
          pass

     def registrar_movimento(self,movimento):
          if not movimento: 
               return None
          self.__historico.append(movimento)

     def encerrar(self):

          if self.estado == "Fechada":
               raise ContaEncerradaError("A conta já está fechada!") 
          
          if self.saldo != 0:
               raise ContaNaoEncerradaError("Saldo ainda não foi zerado")
          
          self.estado = "Fechada"
          movimento = Movimento("Encerramento", "Sucesso", data_atual)
          self.registrar_movimento(movimento)

          cursor.execute("""
          UPDATE conta SET estado = "Fechada"
          WHERE numero = ?
          """, (self.numero,))

          cursor.execute("""
               INSERT INTO historico(numero_conta,operacao,status,data,valor)
               VALUES(?,"Encerramento","Sucesso",?,0)
               """, (self.numero, data_atual,))
          conexao.commit()

          return True
              
     def re_abertura(self):
          if self.estado != "Ativa":
               self.estado = "Ativa"
               cursor.execute("""
                    INSERT INTO historico(numero_conta,operacao,status,data,valor)
                    VALUES(?,"Re-Abertura","Sucesso",?,0)
                    """, (self.numero, data_atual,))
               
               cursor.execute("""
                         UPDATE conta SET estado = "Ativa"
                         WHERE numero = ?
                         """, (self.numero,))
               conexao.commit() 
               return True
          else:
               return None
          
     def extrato(self):
          saldo_formatado = locale.format_string("%.2f", self.saldo, grouping=True)
          return f"""
Conta: {self.numero}
Titular: {self.cliente.nome} 
Tipo: {self.tipo}
Estado: {self.estado}
-------------------------------------------------
Movimentações

{self.extrato_movimento()}
--------------------------------------------------
Saldo Atual........................ R$ {saldo_formatado}
                    """
     def extrato_movimento(self):
               extrato = ""
               for movimento in self.historico:
                    extrato += str(movimento) + "\n \n" 
                    
     
               return extrato 

     def consultar_movimentos(self):
        cursor.execute("SELECT * FROM historico")
        
     
class Conta_Corrente(Conta):
     tarifa = 6.5
     def __init__(self, cliente, numero):
          super().__init__(cliente, numero)

     def calcular_tarifa(self, valor):
          if valor <= 0:
               return None
          
          total = valor + self.__class__.tarifa 

          return total



class Conta_Poupanca(Conta):
     tarifa = 3.25
     def __init__(self, cliente, numero):
          super().__init__(cliente, numero)
          self.saques_realizados = 0
          self.data_saques = data_atual
     
     def calcular_tarifa(self, valor):
          if valor <= 0:
               return None
          
          if self.saques_realizados < 3:
               return valor
          total = valor + self.__class__.tarifa 
          return total

     def sacar(self, valor):
          if self.saques_realizados > 3:
               raise BancoError("Acabou o limite de saca por dia")
          sucesso = super().sacar(valor)
          if sucesso:
               self.saques_realizados += 1
          
          return sucesso
     
class Conta_Universitaria(Conta):
     tarifa = 1.12
     def __init__(self, cliente, numero):
          super().__init__(cliente, numero)
          self.credito_disponivel = 200

     def calcular_tarifa(self, valor):
          if valor <= 0:
               raise ValueError("Digito Inválido")
          
          total = valor + self.__class__.tarifa 

          return total
     def saldo_disponivel(self):
          return self.saldo + self.credito_disponivel
     def sacar(self, valor):
          #if isinstance(valor, str): 
          #     raise ValueError("Você não digitou números")
          if valor > self.saldo and valor > self.credito_disponivel:
               raise SaldoInsuficienteError("Saldo insuficiente, e credito insuficientes")
          
          if valor > self.saldo: 
               
               if self.saldo < 0:
                    if self.credito_disponivel >= valor: 
                         saldo_atual = self.saldo 
                         self.saldo = self.credito_disponivel 
                         sucesso = super().sacar(valor) 
                         if sucesso:
                              self.credito_disponivel -= valor 
                              self.saldo = (saldo_atual - valor) 
                         return sucesso    

               emprestismo = valor - self.saldo  # 100 - 50 = 50
               if self.credito_disponivel < emprestismo: 
                    raise CreditoInsuficienteError("Caro, O crédito dísponivel não é suficiente")
               self.credito_disponivel -= emprestismo
               self.saldo += emprestismo 
               sucesso = super().sacar(valor)  
               if sucesso: 
                    self.saldo -= emprestismo
               return sucesso
          
          return super().sacar(valor) 
     
class Fabrica_de_Contas():
     def restaurar_conta(banco, dados): #{"Tipo": "Conta_Corrente"}
          
          fabrica_de_contas = { 
               "Conta_Corrente": Conta_Corrente,
               "Conta_Poupanca": Conta_Poupanca,
               "Conta_Universitaria": Conta_Universitaria
          }
          cliente = banco.buscar_cliente(dados["Cliente"]) # Retorna o cliente 
          
          classe_nova = fabrica_de_contas[dados["Tipo"]] # Conta_Corrente()

          conta_n = classe_nova.de_dict(dados)

          conta_n.cliente = cliente
          conta_n.saldo = dados["Saldo"]
          conta_n.estado = dados["Estado"]

          return conta_n
     
     def fabricar_conta(tipo):
          fabrica_de_contas = { 
               "Conta_Corrente": Conta_Corrente,
               "Conta_Poupanca": Conta_Poupanca,
               "Conta_Universitaria": Conta_Universitaria
          }
          
          classe_conta = fabrica_de_contas.get(tipo, None)

          return classe_conta

          


     






