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


class testes_Banco(unittest.TestCase):
    def setUp(self):
        apagar_dados_listas_sqlite()
        self.banco = Banco("Nubank")
        self.endereco = Endereco("Jairo Nunes","Metropol", "Criciuma", "8882424")
        self.endereco1 = Endereco("Rua Interlagos","Recanto Verde", "Criciuma", "8881010")
        self.cliente = Cliente("Carlos", 11407147242, 92995096070, self.endereco)
        self.cliente1 = Cliente("Rafaela", 11012030412, 48329134242, self.endereco1)

        self.banco.cadastrar_cliente(self.cliente1)
                
    def test_cadastrar_cliente_com_sucesso(self):
        cliente = self.banco.cadastrar_cliente(self.cliente) # Faz o cadastro
        cliente_encontrado = self.banco.buscar_cliente(cliente.cpf) #Procuramos cliente na basse de dados
        self.assertEqual(cliente.cpf, cliente_encontrado.cpf)

    def test_cadastrar_cliente_ja_cadastrado_lanca_excecao(self): 
        with self.assertRaises(BancoError):
            self.banco.cadastrar_cliente(self.cliente1)

    def test_abrir_conta_com_sucesso(self):
        conta = self.banco.abrir_conta(self.cliente1, "Conta_Poupanca")
        conta_encontrada = self.banco.buscar_conta(conta.numero)

        self.assertEqual(conta.numero, conta_encontrada.numero)

    def test_abrir_conta_com_cliente_nao_cadastrado_lanca_excecao(self):

        with self.assertRaises(ClienteNaoEncontradoError):
            self.banco.abrir_conta(self.cliente, "Conta_Corrente")

    def test_abrir_conta_cadastrada_ao_usuario_lanca_exceao(self):
        self.banco.abrir_conta(self.cliente1, "Conta_Corrente")

        with self.assertRaises(MesmaContaError):
            self.banco.abrir_conta(self.cliente1, "Conta_Corrente")

    def test_abrir_conta_com_um_tipo_nao_existente_lanca_excecao(self):

        with self.assertRaises(BancoError):
            self.banco.abrir_conta(self.cliente1, "Conta_Universal")

    def test_buscar_cliente_reconstruir_cliente_certo(self):
        
        cliente = self.banco.buscar_cliente(self.cliente1.cpf)
        self.assertEqual(self.cliente1.nome, cliente.nome)
        self.assertEqual(self.cliente1.cpf, cliente.cpf)
        self.assertEqual(self.cliente1.phone, cliente.phone)
        #Camada de comprovação do endereço
        self.assertEqual(self.cliente1.endereco.rua, cliente.endereco.rua)
        self.assertEqual(self.cliente1.endereco.bairro, cliente.endereco.bairro)
        self.assertEqual(self.cliente1.endereco.cidade, cliente.endereco.cidade)
        self.assertEqual(self.cliente1.endereco.cep, cliente.endereco.cep)

    def test_buscar_conta_reconstroi_conta_certa(self):
        conta_nova = self.banco.abrir_conta(self.cliente1, "Conta_Corrente")
        conta_encontrada = self.banco.buscar_conta(conta_nova.numero)

        self.assertEqual(conta_nova.cliente.nome, conta_encontrada.cliente.nome)
        self.assertEqual(conta_nova.numero, conta_encontrada.numero)
        self.assertEqual(conta_nova.tipo, conta_encontrada.tipo)
        self.assertEqual(conta_nova.saldo, conta_encontrada.saldo)
        self.assertEqual(conta_nova.estado, conta_encontrada.estado)

        #Não consultamos o historico porque uma conta que esta zerada sem movimentos.
        
        