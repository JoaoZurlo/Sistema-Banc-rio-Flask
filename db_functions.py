import mysql.connector
from mysql.connector import errorcode
import random

def conectar_mysql():
    try:
        conn = mysql.connector.connect(
            user='Joao',
            password='182246',
            host='localhost',
            database='banco'
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: Nome de usuário ou senha incorretos")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Erro: Banco de dados não existe")
        else:
            print(err)
        return None

def gerar_numero_conta():
    return str(random.randint(10000, 99999))

# Exemplo de uso das funções conectar_mysql() e gerar_numero_conta():
def main():
    # Conectar ao MySQL
    conn = conectar_mysql()
    if conn:
        print("Conexão bem-sucedida ao MySQL!")
        conn.close()
    else:
        print("Falha ao conectar ao MySQL.")

    # Gerar um número de conta aleatório
    numero_conta = gerar_numero_conta()
    print(f"Número de conta gerado: {numero_conta}")

if __name__ == "__main__":
    main()


