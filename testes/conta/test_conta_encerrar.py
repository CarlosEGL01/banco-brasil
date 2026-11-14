import os
os.environ["BANCO_DB_PATH"] = "banco-testes.db"

import unittest
from conta import Conta_Corrente
from cliente import Cliente, Endereco
from excecoes import ContaEncerradaError, ContaNaoEncerradaError
from database import apagar_dados_sqlite
from banco import Banco


class TestConta(unittest.TestCase):
    def setUp(self):
        apagar_dados_sqlite() #Apagamos os dados antes
        self.banco = Banco("Nunbak")
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", 8881010)
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.banco.cadastrar_cliente(self.cliente)
        self.conta = self.banco.abrir_conta(self.cliente, "Conta_Corrente")


    def test_encerrar_conta_com_sucesso(self):
        conta = self.banco.encerrar_conta(1)
        self.assertEqual(conta.estado, "Fechada")

    def test_encerrar_conta_ja_encerrada_lanca_excecao(self):
        self.banco.encerrar_conta(1)
        with self.assertRaises(ContaEncerradaError):
            self.banco.encerrar_conta(1)

    def test_encerrar_conta_com_saldo_lanca_excecao(self):
        self.conta.depositar(100)
        with self.assertRaises(ContaNaoEncerradaError):
            self.banco.encerrar_conta(1)
        

