import sqlite3
import os

CAMINHO_BANCO = os.getenv("BANCO_DB_PATH", "banco.db")

conexao = sqlite3.connect(
    CAMINHO_BANCO,
    check_same_thread=False
)
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()

print("BANCO UTILIZADO:", CAMINHO_BANCO)

def apagar_dados_sqlite():
    caminho_teste = os.path.abspath("banco-testes.db")
    caminho_atual = os.path.abspath(CAMINHO_BANCO)

    if caminho_atual != caminho_teste:
        raise PermissionError(
            "Limpeza permitida somente no banco de testes!"
        )
    cursor.execute("DELETE FROM endereco")
    cursor.execute("DELETE FROM historico")
    cursor.execute("DELETE FROM historico_transferencia")
    cursor.execute("DELETE FROM conta")
    cursor.execute("DELETE FROM cliente")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'historico'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'cliente'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'endereco'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'historico_transferencia'")
    conexao.commit()