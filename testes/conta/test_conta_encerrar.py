import unittest
from conta import Conta_Corrente
from cliente import Cliente, Endereco
from excecoes import ContaEncerradaError, ContaNaoEncerradaError



class TestConta(unittest.TestCase):
    def setUp(self):
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", 8881010)
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.conta = Conta_Corrente(self.cliente, 1)


    def test_encerrar_conta_com_sucesso(self):
        self.conta.encerrar()
        self.assertEqual(self.conta.estado, "Fechada")

    def test_encerrar_conta_ja_encerrada_lanca_excecao(self):
        self.conta.encerrar()
        with self.assertRaises(ContaEncerradaError):
            self.conta.encerrar()

    def test_encerrar_conta_com_saldo_lanca_excecao(self):
        self.conta.depositar(100)
        with self.assertRaises(ContaNaoEncerradaError):
            self.conta.encerrar()
        

