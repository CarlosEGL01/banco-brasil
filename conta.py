from abc import ABC, abstractmethod
from movimento import Movimento, Movimento_Deposito, Movimento_Saque, Fabrica_de_Movimento
from excecoes import SaldoInsuficienteError, ContaEncerradaError, BancoError, CreditoInsuficienteError, ContaNaoEncerradaError, ContaNaoEncontradaError
import locale

from datetime import datetime, date
import database as banco
# Define a configuração para o padrão do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

import sqlite3


#Horario
hoje = date.today()
data_atual = datetime.strftime(hoje, "%d/%m/%Y")



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
     @historico.setter
     def historico(self, valor):
          self.__historico = valor
     
     def depositar(self,valor):
          if self.estado != "Ativa":
               raise ContaEncerradaError("Não pode fazer esse movimento. CONTA ENCERRADA!")
          
          if isinstance(valor, str):
               raise ValueError("Digite um número")
          
          if valor <= 0:
               raise ValueError("Digite um numero válido")
          
          elif valor > 0:
               total = self.__saldo + valor
               try:
                    banco.cursor.execute("""
                         UPDATE conta
                         SET saldo = ?
                         Where numero = ?
                    """, (total, self.numero,))
                    #Essa linha de comando conferi se houve uma alteração na linha do SQL, caso contrario fosse 0 não permite inserir o registro no historico
                    if banco.cursor.rowcount != 1:
                         raise ContaNaoEncontradaError("Não foi possível atualizar a conta.")
                    
                    banco.cursor.execute("""
                         INSERT INTO historico(numero_conta, operacao,status,data,valor)
                         VALUES(?,"Deposito", "Sucesso", ?, ?)
                    """, (self.numero,data_atual,valor,))
                    banco.conexao.commit()
               except sqlite3.Error as e:
                    print(e)
                    banco.conexao.rollback()
                    raise
               
               self.__saldo += valor
               novo_movimento = Movimento_Deposito("Deposito","Sucesso",data_atual, valor)
               self.registrar_movimento(novo_movimento)

          return self
          

     def sacar(self,valor): 
          if self.estado != "Ativa":
               raise ContaEncerradaError("Não pode fazer esse movimento. CONTA ENCERRADA!")
          if isinstance(valor, str) or valor <= 0 :
               raise ValueError("Número Inválido")
          if valor > self.__saldo: 
               raise SaldoInsuficienteError("Não tem saldo para tirar esse valor")
          if valor == self.__saldo: ## É para vaziar conta e poder encerrar
               total = valor
          else:
               total = self.calcular_tarifa(valor) 
          
          if total <= self.__saldo:  
               total_final = self.__saldo - total
               try:
                    #Guardando operação
                    banco.cursor.execute("UPDATE conta SET saldo = ? WHERE numero = ?", (total_final, self.numero))
                    if banco.cursor.rowcount != 1:
                         raise ContaNaoEncontradaError("Não foi possivel atualizar a conta.")
                    #HISTORICO AO SQL
                    banco.cursor.execute("""
                         INSERT INTO historico(numero_conta,operacao,status,data,valor)
                         VALUES(?,"Saque","Sucesso",?,?)
                    """, (self.numero, data_atual, total,))
                    banco.conexao.commit()
               except sqlite3.Error as e:
                    print(e)
                    banco.conexao.rollback()
                    raise
               self.__saldo -= total
               novo_movimento = Movimento_Saque("Saque","Sucesso",data_atual, total) 
               self.registrar_movimento(novo_movimento)
               
          return self

     def consultar_historico(self,tipo=""):
          if tipo == "":
               banco.cursor.execute("SELECT * FROM historico WHERE numero_conta = ?", (self.numero,))
               resultado_movimentos = banco.cursor.fetchall()
               return resultado_movimentos

          if tipo == "Transferencia Recebida" or tipo == "Transferencia Enviada":

               banco.cursor.execute("""
                         SELECT * FROM historico_transferencia
                         WHERE numero_conta = ? AND operacao = ?
                         """, (self.numero, tipo,))
               resultado_movimentos = banco.cursor.fetchall()
               return resultado_movimentos
          
          banco.cursor.execute("""
          SELECT * FROM historico
          WHERE numero_conta = ? AND operacao = ?
          """, (self.numero, tipo,))

          resultado_movimentos = banco.cursor.fetchall()

          return resultado_movimentos

     
     def saldo_disponivel(self):
          return self.saldo #Num X

     def informacoes(self):
          banco.cursor.execute("""
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

          return banco.cursor.fetchone()

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

          try:
               banco.cursor.execute("""
               UPDATE conta SET estado = "Fechada"
               WHERE numero = ?
               """, (self.numero,))
               if banco.cursor.rowcount != 1:
                    raise ContaEncerradaError("Deu um erro no encerramento!")
               
               banco.cursor.execute("""
                    INSERT INTO historico(numero_conta,operacao,status,data,valor)
                    VALUES(?,"Encerramento","Sucesso",?,0)
                    """, (self.numero, data_atual,))
               banco.conexao.commit()
          except Exception:
               banco.conexao.rollback()
               raise
          
          self.estado = "Fechada"
          movimento = Movimento("Encerramento", "Sucesso", data_atual)
          self.registrar_movimento(movimento)

          return self
              
     def re_abertura(self):
          if self.estado == "Ativa":
               raise ContaNaoEncerradaError("Essa conta já esta ativa!")
          try:
               banco.cursor.execute("""
                         UPDATE conta SET estado = "Ativa"
                         WHERE numero = ?
                         """, (self.numero,))
               if banco.cursor.rowcount != 1:
                    raise ContaNaoEncontradaError("Não conseguimos localizar a conta e atualizar o estatus")
                    
               banco.cursor.execute("""
                         INSERT INTO historico(numero_conta,operacao,status,data,valor)
                         VALUES(?,"Re-Abertura","Sucesso",?,0)
                         """, (self.numero, data_atual,))
               banco.conexao.commit()
          except Exception:
               banco.conexao.rollback()
               raise 
               

          self.estado = "Ativa"
          movimento = Movimento("Re-abertura", "Sucesso", data_atual)
          self.registrar_movimento(movimento)
          return self
          
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
          if isinstance(valor, str) or valor <= 0: 
               raise ValueError("Você não digitou números")
          if self.estado != "Ativa":
               raise ContaEncerradaError("Não pode fazer esse movimento. CONTA ENCERRADA!")
          
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

     @classmethod
     def fabricar_conta_completa(cls, conta, cliente):

          classe_conta = cls.fabricar_conta(conta[2])

          conta_final = classe_conta(cliente, conta[0])
          #Restaurando os estados da conta:
          conta_final.saldo = conta[3] 
          conta_final.estado = conta[4]

          historico = Fabrica_de_Movimento.restaurar_historico(conta[0])

          conta_final.historico = historico
     
          return conta_final

          


     






