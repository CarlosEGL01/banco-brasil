import unittest
from banco import Banco
from cliente import Cliente, Endereco
from excecoes import BancoError, ClienteNaoEncontradoError, MesmaContaError, ContaNaoEncontradaError, SaldoInsuficienteError
from conta import Fabrica_de_Contas
import sqlite3

conexao = sqlite3.connect("banco.db")

cursor = conexao.cursor()
conexao.execute("PRAGMA foreign_key = ON")


def apagar_dados_listas_sqlite():
    cursor.execute("DELETE FROM cliente")
    cursor.execute("DELETE FROM endereco")
    cursor.execute("DELETE FROM conta")
    cursor.execute("DELETE FROM historico")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'historico'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'cliente'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'endereco'")
    conexao.commit()


#TEST TRANSFERENCIAS
class testes_transferencia(unittest.TestCase):
    def setUp(self):
        apagar_dados_listas_sqlite()

        self.banco = Banco("Nubank")
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", 8882424)
        self.endereco1 = Endereco("Rua Interlagos","Recanto Verde", "Criciuma", 8881010)
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.cliente1 = Cliente("Rafaela", 11012030412, 48329134242, self.endereco1)
        
        self.banco.cadastrar_cliente(self.cliente)
        self.banco.cadastrar_cliente(self.cliente1)
        self.conta_x = self.banco.abrir_conta(self.cliente,"Conta_Corrente")
        self.conta_z = self.banco.abrir_conta(self.cliente1, "Conta_Corrente")

        self.conta_x.depositar(1000)
        self.conta_z.depositar(329.30)


    def criar_cliente(self):
        endereco = Endereco("Luis", "Sao Luiz", "Imaginação", 3333333)
        cliente = Cliente("Eduard", 11111111, 2222222, endereco)

        return cliente


    def test_transferencia_com_sucesso(self):
        
        saldo_x_atual = self.conta_x.saldo # 1000
        saldo_z_atual = self.conta_z.saldo # 329.30
        valor = 150
        self.banco.transferencia(1,2,valor)
        
        conta_x = self.banco.buscar_conta(1)
        conta_z = self.banco.buscar_conta(2)
        self.assertEqual(conta_x.saldo, (saldo_x_atual - valor))
        self.assertEqual(conta_z.saldo, (valor + saldo_z_atual))

    def test_transferencia_falho_saldo_insuficiente_error(self):
        with self.assertRaises(SaldoInsuficienteError):
            self.banco.transferencia(1,2,1200)

    def test_transferencia_valor_invalido(self):
        with self.assertRaises(ValueError):
            self.banco.transferencia(1,2,-100)

    def test_transferencia_conta_origem_nao_encontrada(self):
        conta_inexestente_numero = 10
        with self.assertRaises(ContaNaoEncontradaError):
            self.banco.transferencia(conta_inexestente_numero, 1, 100)

    def test_transferencia_conta_destino_nao_encontrada(self):
        conta_inexestente_numero = 10
        with self.assertRaises(ContaNaoEncontradaError):
            self.banco.transferencia(1, conta_inexestente_numero, 100)

    def test_transferencia_mesmo_tipo_de_conta(self):
        with self.assertRaises(BancoError):
            self.banco.transferencia(1,1,120)

    def test_registrou_movimento_na_conta_origem(self):
        self.banco.transferencia(1,2,250)
        #ACHAR O MOVIMENTO DE TRANSFERENCIA RECIBIDA
        conta_1 = self.banco.buscar_conta(1) 
        resultado_conta1 = conta_1.consultar_historico("Transferencia Enviada")
        ultimo_movimento = resultado_conta1[-1]
        print(ultimo_movimento)
            
        self.assertEqual(ultimo_movimento[2], "Transferencia Enviada")


    def test_registrou_movimento_na_conta_destino(self):
        self.banco.transferencia(1,2,250)
        #ACHAR O MOVIMENTO DE TRANSFERENCIA RECIBIDA
        conta_2 = self.banco.buscar_conta(2) 
        resultado_conta2 = conta_2.consultar_historico("Transferencia Recebida")
        ultimo_movimento = resultado_conta2[-1]
                
        self.assertEqual(ultimo_movimento[2], "Transferencia Recebida")