from cliente import Cliente, Endereco
from conta import Conta
from banco import Banco
from datetime import date
from excecoes import SaldoInsuficienteError, ContaEncerradaError, ContaNaoEncerradaError, CreditoInsuficienteError, ContaNaoEncontradaError, BancoError

class repositorioJSON():
    pass

banco_do_brasil = Banco("Banco Do Brasil")

endereco_cliente1 = Endereco("Jairo Nunes", "Metropol","Criciuma","878001")
endereco_cliente2 = Endereco("Alvaro Catao", "Minera","Criciuma","878020")
endereco_cliente3 = Endereco("Sebastão Toledo", "Operaria","Criciuma","878110")
endereco_cliente4 = Endereco("Oadi Matheus Silvano", "Maria Ceu","Criciuma","888101")
endereco_cliente5 = Endereco("Interlagos", "Recanto Verde","Criciuma","888150")
endereco_cliente6 = Endereco("Joao Milioli", "Santa Barbara","Criciuma","899910")

cliente1 = Cliente("Carlos Gutierrez", 27656326, 4249305444,endereco_cliente1)
cliente2 = Cliente("Rafaela Gomes", 11023040, 4819323943,endereco_cliente2)
cliente3 = Cliente("Gerson Lopez", 25454325, 4261898102,endereco_cliente3)
cliente4 = Cliente("Joao Cancelo", 11235545, 4856123647,endereco_cliente4)
cliente5 = Cliente("Lucas Paqueta", 16158963, 4819323941,endereco_cliente5)
cliente6 = Cliente("Memphis Depay", 78981236, 4261898102,endereco_cliente6)

banco_do_brasil.cadastrar_cliente(cliente1)

banco_do_brasil.cadastrar_cliente(cliente2)
banco_do_brasil.cadastrar_cliente(cliente3)
banco_do_brasil.cadastrar_cliente(cliente4)
banco_do_brasil.cadastrar_cliente(cliente5)
banco_do_brasil.cadastrar_cliente(cliente6)
cliente_fake = Cliente("Pedro",12103130,1314131,endereco_cliente1)

banco_do_brasil.abrir_conta(cliente1, "Conta_Corrente")
banco_do_brasil.abrir_conta(cliente2, "Conta_Poupanca")
banco_do_brasil.abrir_conta(cliente3, "Conta_Universitaria")
banco_do_brasil.abrir_conta(cliente4, "Conta_Corrente")
banco_do_brasil.abrir_conta(cliente5, "Conta_Poupanca")
banco_do_brasil.abrir_conta(cliente6, "Conta_Universitaria")
#print(banco_do_brasil.abrir_conta(cliente_fake))

conta1 = banco_do_brasil.encontrar_conta(1)
conta2 = banco_do_brasil.encontrar_conta(2)
conta3 = banco_do_brasil.encontrar_conta(3)
conta4 = banco_do_brasil.encontrar_conta(4)
conta5 = banco_do_brasil.encontrar_conta(5)
conta6 = banco_do_brasil.encontrar_conta(6)
conta1.depositar(20000)
conta1.sacar(10500)

conta2.depositar(15000)
conta2.sacar(7500)

conta3.depositar(12000)
#conta3.sacar(6450)

conta4.depositar(10000)
conta4.sacar(5830)

conta5.depositar(5000)
conta5.sacar(3360)



#banco_do_brasil.encerrar_conta(6)

#banco_do_brasil.transferencia(1,2,300)


#banco_do_brasil.salvar_json("banco_do_brasil")

#banco_do_brasil = banco_do_brasil.carregar_json("banco_do_brasil")


print(conta1.extrato())


print(len(banco_do_brasil.clientes))



