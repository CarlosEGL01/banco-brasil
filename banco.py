from conta import Conta, Fabrica_de_Contas
from movimento import Movimento_Transferencia, Fabrica_de_Movimento
from cliente import Cliente, Endereco
from excecoes import BancoError, ClienteNaoEncontradoError, ContaNaoEncontradaError, ContaNaoEncerradaError, MesmaContaError, SaldoInsuficienteError

data_atual = "12/08/2026"

import json
import sqlite3
conexao = sqlite3.connect("banco.db")
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()



class Banco:
    def __init__(self, nome):
        self.nome = nome
        self.contas = []
        self.clientes = []
        self.proximo = 0

    def __str__(self):
        return f"Banco: {self.nome}" 
    
    def __iter__(self):
        return iter(self.contas)
    
    
    def __len__(self):
        return len(self.contas)
    
    
    def para_dict(self):
        return{
            "Nome": self.nome,
            "Contas": [conta.para_dict() for conta in self.contas],
            "Clientes": [cliente.para_dict() for cliente in self.clientes],
            "Num_Proximo": self.proximo
        }
    @classmethod
    def de_dict(cls,dados):
        return cls(dados["Nome"])
    
    def salvar_json(self,arquivo):
         with open(arquivo, "w") as f:
            json.dump(self.para_dict(), f, indent=4)
            

    @classmethod
    def carregar_json(cls,arquivo):
        with open(arquivo, "r") as f:
            dados_banco = json.load(f)

        banco = cls(dados_banco["Nome"])
        banco.proximo = dados_banco["Num_Proximo"]

        for cliente in dados_banco["Clientes"]:
            cliente_n = Cliente.de_dict(cliente)
            banco.cadastrar_cliente(cliente_n)
            
        for conta in dados_banco["Contas"]:
            conta_nova = Fabrica_de_Contas.restaurar_conta(banco,conta)

            for movimento in conta["Historico"]:
                movimento_novo = Fabrica_de_Movimento.resturar_movimento(movimento)
                conta_nova.registrar_movimento(movimento_novo)
                        
            banco.contas.append(conta_nova)
        
        return banco
                
    """  
    def relatorio(self):
        return {
            "Clientes": self.total_clientes(),
            "Contas": len(self.contas),
            "Ativas": self.total_contas_aberta(),
            "Encerradas": self.total_contas_encerradas(),
            "Saldo Total": self.total_saldo(),
            "Movimentos totais": self.movimentos_das_contas()
        }
    
    
    
    def total_contas_aberta(self):
        abertas = [conta for conta in self.contas if conta.estado == "Ativa"]

        return len(abertas)
        
    def total_contas_encerradas(self):
        encerradas = [conta for conta in self.contas if conta.estado == "Encerrada"]
        return len(encerradas)
    """
    ##CONSULTAS SQLITE
    def total_contas(self):
        cursor.execute("SELECT COUNT(*) FROM conta")
        total = cursor.fetchone()[0]
        return total
    
    def total_clientes(self):
        cursor.execute("SELECT COUNT(*) FROM cliente")
        total = cursor.fetchone()[0]
        return total

    def total_contas_estado(self,estado):
        cursor.execute("""
            SELECT COUNT(*) 
            FROM CONTA
            WHERE estado = ?
        """, (estado,))

        return cursor.fetchone()[0]

    def total_saldo(self):
            cursor.execute("SELECT SUM(conta.saldo) AS saldo_total FROM conta ")
            return cursor.fetchone()[0]
    
    def total_movimentos(self):
        cursor.execute("SELECT COUNT(*) FROM historico")

        return cursor.fetchone()[0]  
    
    ##RELATORIOS APLICANDO CONSULTAS SQLITE
    def relatorio(self):
        return {
            "Clientes": self.total_clientes(),
            "Contas": self.total_contas(),
            "Ativas": self.total_contas_estado("Ativa"),
            "Fechadas": self.total_contas_estado("Fechadas"),
            "Saldo": self.total_saldo(),
            "Movimentos": self.total_movimentos()

        }

    def relatorio_analitico(self):

        cursor.execute("""
            WITH contas_ativas AS(
                SELECT *
                FROM conta
                WHERE conta.estado = "Ativa"
            )
            SELECT 
            cliente.numero,
            cliente.nome,
            COUNT(*) AS TOTAL_CONTAS_ATIVAS,
            SUM(contas_ativas.saldo) AS TOTAL_SALDO_CONTAS,
            CASE
                WHEN SUM(contas_ativas.saldo) >= 5000  THEN "SALDO ALTO"
                WHEN SUM(contas_ativas.saldo) >= 3000  THEN "SALDO MEDIO"
                ELSE "SALDO BAIXO"
            END AS CATEGORIA     
            FROM contas_ativas
            JOIN cliente 
                ON contas_ativas.cliente_numero = cliente.numero
            GROUP BY cliente.numero, cliente.nome
            ORDER BY TOTAL_SALDO_CONTA DESC
        """)

        
        resultado = cursor.fetchall()
        return resultado
    
    def buscar_cliente_letra(self, letra=""):

        if letra == "":
            cursor.execute("""
                SELECT *
                FROM cliente
            """)
            return cursor.fetchall()
        letra  += "%"
        cursor.execute("""
            SELECT *
            FROM cliente
            WHERE nome LIKE ?
        """, (letra,))

        return cursor.fetchall()

    def media_salario(self):
        cursor.execute("SELECT AVG(saldo) FROM conta")
        return cursor.fetchone()[0]




    def contas_categoria_salarios(self,categoria):
        cursor.execute("""WITH conta_saldo_maior AS (
            SELECT *,
            
            CASE 
                WHEN conta.saldo >= 5000  AND  conta.estado = "Ativa" THEN "Saldo Alto"
                WHEN conta.saldo >= 3000 AND  conta.estado = "Ativa" THEN "Saldo Medio"
                ELSE "Saldo Baixo"
            END as categoria
            FROM conta
            )

            SELECT 
            conta_saldo_maior.numero,
            cliente.nome,
            cliente.cpf,
            conta_saldo_maior.tipo,
            conta_saldo_maior.saldo,
            conta_saldo_maior.estado,
            conta_saldo_maior.categoria
            FROM conta_saldo_maior
            JOIN cliente ON conta_saldo_maior.cliente_numero = cliente.numero
            WHERE conta_saldo_maior.categoria = ?
        

        """, (categoria,))
        

        return cursor.fetchall()
    
    def encerrar_conta(self,num_conta):
        conta = self.buscar_conta(num_conta)

        if conta is None:
            raise ContaNaoEncontradaError("Não encontramos a conta no sistema.")
        
        conta.encerrar()
        return True
    
    def movimentos_das_contas(self):
        total_movimentos = 0

        for conta in self.contas:
            if conta.estado == "Ativa":
                total_movimentos += len(conta.historico)
        
        return total_movimentos
   
    def buscar_conta(self,num):
        cursor.execute("SELECT * FROM conta WHERE numero = ?", (num,))
        resultado_conta = cursor.fetchone()
        if resultado_conta is None:
            return None
        cursor.execute("SELECT * FROM cliente WHERE numero = ?", (resultado_conta[1],))
        cpf_cliente = cursor.fetchone()[2]

        resultado_cliente = self.buscar_cliente(cpf_cliente) #Retorna objeto 

        conta_class = Fabrica_de_Contas.fabricar_conta(resultado_conta[2])
        if conta_class is None:
            return None
       
        conta = conta_class(resultado_cliente,num)

        conta.estado = resultado_conta[4]
        conta.saldo = resultado_conta[3]
        
        return conta


    

    def buscar_contas_cpf(self, cpf):
        cursor.execute("SELECT * FROM conta WHERE cliente_numero IN (SELECT NUMERO FROM cliente WHERE cpf = ?) ",(cpf,))
        return cursor.fetchall()




    
    
    def buscar_cliente(self,cpf_num): #--> MÉTODO NOVO
        cursor.execute("""
        SELECT * from cliente
        WHERE cpf = ?
        """, (cpf_num,))

        resultado_cliente = cursor.fetchone()

        if resultado_cliente is None:
            return None
        
        cursor.execute("""
        SELECT * from endereco
        WHERE cliente_numero = ?
        """, (resultado_cliente[0],))

        resultado_endereco = cursor.fetchone()
        
        endereco = Endereco(resultado_endereco[2], resultado_endereco[3], resultado_endereco[4], resultado_endereco[5])
        cliente = Cliente(resultado_cliente[1], resultado_cliente[2], resultado_cliente[3], endereco)
        return cliente


    def cadastrar_cliente(self, cliente):
        cliente_existente = self.buscar_cliente(cliente.cpf) #Procura o cliente na base de dados
        
        if cliente_existente is None:
            cursor.execute("""
                INSERT INTO cliente(nome, cpf, phone)
                VALUES (?,?,?)
                """, (cliente.nome, cliente.cpf, cliente.phone,))

            cursor.execute("SELECT * FROM  cliente WHERE cpf = ?", (cliente.cpf,))
            resultado_cliente = cursor.fetchone() #Entrega o cliente em uma tupla
            
            cursor.execute("""
                INSERT INTO endereco(cliente_numero, rua, bairro, cidade, cep)
                VALUES (?,?,?,?,?)
                """, (resultado_cliente[0],cliente.endereco.rua, cliente.endereco.bairro, cliente.endereco.cidade, cliente.endereco.cep,))
            conexao.commit()

            cursor.execute("SELECT * FROM  endereco WHERE cliente_numero = ?", (resultado_cliente[0],))
            resultado_endereco = cursor.fetchone() #Entrega o endereco em uma tupla 

            endereco = Endereco(resultado_endereco[2], resultado_endereco[3], resultado_endereco[4], resultado_endereco[5])
            cliente = Cliente(resultado_cliente[1], resultado_cliente[2], resultado_cliente[3], endereco)
            return cliente

        else:
            raise BancoError("Cliente já cadastrado!")

            

            

    def gerar_numero(self):
       
       cursor.execute("""
       SELECT COALESCE(MAX(numero), 0) + 1
       FROM conta
       """)

       return cursor.fetchone()[0]

    def abrir_conta(self, cliente, tipo):

        cliente_existente = self.buscar_cliente(cliente.cpf)

        if cliente_existente is None: #Conferimos se o cliente existe
            raise ClienteNaoEncontradoError(f"O cliente não existe nossa base de dados")

        tipo_existente = self.encontrar_tipo_conta(cliente.cpf, tipo) # O cliente tem o conta? Tem esse mesmo tipo de conta?

        if tipo_existente:
            raise MesmaContaError("O cliente já possui uma conta desse tipo!")
        
        classe_conta = Fabrica_de_Contas.fabricar_conta(tipo) 
        if classe_conta is None: #Conferimos se o tipo de conta foi fabricada e existe
            raise BancoError(f"{tipo} esse tipo não existe")

        num = self.gerar_numero()
        conta_nova = classe_conta(cliente_existente,num)

        cursor.execute("SELECT * FROM cliente WHERE cpf = ? ", (cliente.cpf,))
        cliente_numero = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO conta(numero,cliente_numero, tipo, saldo, estado)
            VALUES (?,?,?,?,?)
        """, (conta_nova.numero, cliente_numero,conta_nova.tipo, conta_nova.saldo,conta_nova.estado,))
        conexao.commit()

        

        return conta_nova #Retorna a conta, desing de API
    
    """def encontrar_tipo_conta(self,cliente, tipo): #Antiguo método 
        cursor.execute("SELECT * FROM cliente WHERE cpf = ? ", (cliente.cpf,))
        cliente_numero = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM conta WHERE cliente_numero = ? and tipo = ?", (cliente_numero, tipo,))
        resultado = cursor.fetchone()
        if resultado is None:
            return None
        return resultado"""

    def encontrar_tipo_conta(self, cpf, tipo): #Método com EXITS E SUBQUERY
        cursor.execute("""SELECT 
            * 
            FROM conta 
            WHERE conta.tipo = ? 
            AND EXISTS(SELECT 1 FROM cliente WHERE cliente.cpf = ? AND cliente.numero = conta.cliente_numero )""", (tipo, cpf, ))
        resultado = cursor.fetchone()
        if resultado is None:
            return None
        return resultado
    
    def transferencia(self,num_origem,num_destino, valor):
        if valor <= 0:
            raise ValueError("Digite um valor válido")
        
        conta_origem = self.buscar_conta(num_origem)
        conta_destino = self.buscar_conta(num_destino)

        if conta_origem is None:
            raise ContaNaoEncontradaError("Conta Origem não encontrada")
        elif conta_destino is None:
            raise ContaNaoEncontradaError("Conta Destino não encontrada") 
                                                                    
    
        if conta_origem.numero == conta_destino.numero:
            raise BancoError("Não pode transferir no mesmo tipo de conta")
        if valor <= conta_origem.saldo: # 200 < 100
            total_saldo_origem = conta_origem.saldo - valor
            total_saldo_destino = conta_destino.saldo + valor

            conta_origem.saldo = total_saldo_origem
     #       print(conta_origem.saldo)
            conta_destino.saldo = total_saldo_destino
     #       print(conta_destino.saldo)
            
            #MODIFICAR ESTADO DO SQL
            try:

                cursor.execute("""
                    UPDATE conta
                    SET saldo = ?
                    WHERE numero = ?
                """, (total_saldo_origem, conta_origem.numero))
                cursor.execute("""
                    UPDATE conta
                    SET saldo = ?
                    WHERE numero = ?
                """, (total_saldo_destino, conta_destino.numero))

                #HISTORICO
                cursor.execute("""
                    INSERT INTO historicO(numero_conta,operacao,status,data,valor)
                    VALUES(?,"Transferencia Enviada","Sucesso",?,?)
                    """, (conta_origem.numero, data_atual,-valor))
                cursor.execute("""
                    INSERT INTO historico(numero_conta,operacao,status,data,valor)
                    VALUES(?,"Transferencia Recebida","Sucesso",?,?)
                    """, (conta_destino.numero, data_atual,valor))
                conexao.commit()
            except sqlite3.Error:
                conexao.rollback()
                raise

            evento_novo = Movimento_Transferencia("Transferencia","Sucesso",data_atual,conta_origem, conta_destino,valor)
            conta_origem.registrar_movimento(evento_novo)
            conta_destino.registrar_movimento(evento_novo)
            return True
        else:
            raise SaldoInsuficienteError("Conta origem tem saldo insuficiente ")

        
    






