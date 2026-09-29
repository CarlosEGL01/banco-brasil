import unittest
from conta import Conta_Corrente
from cliente import Cliente, Endereco
from excecoes import ContaEncerradaError, SaldoInsuficienteError
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


class TestConta(unittest.TestCase):
    def setUp(self):
        apagar_dados_listas_sqlite()
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", 8881010)
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.conta = Conta_Corrente(self.cliente, 1)
        self.conta.depositar(200)
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


