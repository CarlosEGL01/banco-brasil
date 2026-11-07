import unittest
import os
os.environ["BANCO_DB_PATH"] = "banco-testes.db"

from cliente import Cliente, Endereco
from excecoes import ContaEncerradaError
import banco
from banco import Banco


def apagar_dados_listas_sqlite():
    banco.cursor.execute("DELETE FROM endereco")
    banco.cursor.execute("DELETE FROM historico")
    banco.cursor.execute("DELETE FROM historico_transferencia")
    banco.cursor.execute("DELETE FROM conta")
    banco.cursor.execute("DELETE FROM cliente") #Coloco aqui porque ele é a principal chave strangeira, daria error de integridade .
    banco.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'historico'")
    banco.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'cliente'")
    banco.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'endereco'")
    banco.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'historico_transferencia'")
    banco.conexao.commit()



class TestConta(unittest.TestCase):
    def setUp(self):
        apagar_dados_listas_sqlite()
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", 8881010)
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.banco = Banco("Itau")

        self.banco.cadastrar_cliente(self.cliente)
        self.banco.abrir_conta(self.cliente,"Conta_Corrente")

        self.conta = self.banco.buscar_conta(1)
        

    def test_se_conta_estiver_fechada_lanca_excecao(self):
        self.banco.encerrar_conta(1)
        conta_x = self.banco.buscar_conta(1)
        with self.assertRaises(ContaEncerradaError):
            conta_x.depositar(100)

    def test_depositar_com_numero_invalido_lanca_excecao(self):
        with self.assertRaises(ValueError):
            self.conta.depositar(-100)

    def test_depositar_com_caracter_invalido_lanca_excecao(self):
        with self.assertRaises(ValueError):
            self.conta.depositar("100")

    def test_deposito_registra_movimento(self):
        self.conta.depositar(100)
        movimentos = self.conta.consultar_historico("Deposito")
        ultimo_movimento = movimentos[-1]
        self.assertEqual(ultimo_movimento[2], "Deposito")

    def test_deposito_com_sucesso(self):
        self.conta.depositar(100)
        self.assertEqual(self.conta.saldo, 100)