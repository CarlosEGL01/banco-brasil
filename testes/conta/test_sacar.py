import unittest
import os
os.environ["BANCO_DB_PATH"] = "banco-testes.db"

from conta import Conta_Corrente
from cliente import Cliente, Endereco
from excecoes import ContaEncerradaError, SaldoInsuficienteError
from banco import Banco
from database import apagar_dados_sqlite


class TestConta(unittest.TestCase):
    def setUp(self):
        apagar_dados_sqlite() #Apagamos os dados antes
        self.banco = Banco("Nunbak")
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", 8881010)
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.banco.cadastrar_cliente(self.cliente)
        self.conta = self.banco.abrir_conta(self.cliente, "Conta_Corrente")
        
        self.conta.depositar(200)
    def tearDown(self):
        apagar_dados_sqlite() #Apagamos os dados depois para deixar zerada as tabelas
    def test_sacar_dinheiro_conta_encerrada_lanca_excecao(self):
        self.conta.saldo = 0 #Segundo meu programa uma conta encerrada deveria estar zerada.
        self.conta.encerrar() 
        with self.assertRaises(ContaEncerradaError):
            self.conta.sacar(200)
    def test_sacar_dinheiro_com_sucesso(self):
        valor = 200 ## Tem que ser menor ou igual ao saldo(200)
        saldo_esperado = self.conta.saldo - valor
        self.assertTrue(self.conta.sacar(valor)) 
        self.assertEqual(self.conta.saldo, saldo_esperado)

    def test_sacar_dinheiro_valor_invalido_lanca_excecao(self):
        with self.assertRaises(ValueError):
            self.conta.sacar(-100)

    def test_sacar_dinheiro_saldo_insuficiente_lanca_excecao(self):
        with self.assertRaises(SaldoInsuficienteError):
            self.conta.sacar(300) #300 > 200 Vai dar certo ;)

    def test_sacar_dinheniro_com_sucesso_registra_movimento(self):
        self.conta.sacar(100)
        movimentos = self.conta.consultar_historico("Saque")
        ultimo_movimento = movimentos[-1]
        self.assertEqual(ultimo_movimento[2], "Saque")


