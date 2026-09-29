import sqlite3
from banco import Banco
from conta import Conta

"""
try:
    with sqlite3.connect("banco.db") as conexao:
        conexao.execute("PRAGMA foreign_keys = ON")
        cur = conexao.cursor()
        cur.execute("UPDATE conta set saldo = 2250 WHERE numero = 1")#Primeira alteração feita
        cur.execute("UPDATE conta set saldoo = 1000 WHERE numero = 1")#Alteração com error
        resultado = cur.fetchmany(1)
        print(resultado) 
except sqlite3.Error:
    
        cur.execute("SELECT * FROM conta")

        resultado = cur.fetchmany(1)# O estado do saldo volta ao original 
        print("Chegou except")
        print(resultado) 
"""

try:
    with sqlite3.connect("banco.db") as conexao:
        conexao.execute("PRAGMA foreign_keys = ON")
        cur = conexao.cursor()

        itau = Banco("Itau")

        relatorio_analitico = itau.relatorio_analitico()

        for item in relatorio_analitico:
            print(f"Cliente Numero: {item[0]}")
            print(f"Cliente Nome: {item[1]}")
            print(f"Contas Ativas: {item[2]}")
            print(f"Saldo Total: {item[3]} R$")
            print(f"Categoria: {item[4]}")
            print("\n")
    
except sqlite3.Error as e:
    print("Chegamos")
    print(e)

else:
    print("Sucesso")

finally:
    print("Finalizamos")
    conexao.close()
        




    

        
