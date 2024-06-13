from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import errorcode
import random
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

def conectar_mysql():
    try:
        conn = mysql.connector.connect(
            user=os.environ.get('DB_USER', 'Joao'),
            password=os.environ.get('DB_PASSWORD', '182246'),
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'banco')
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

@app.route('/')
def index():
    numero_conta = gerar_numero_conta()
    return render_template('index.html', numero_da_conta=numero_conta)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = conectar_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT numero_da_conta FROM Banco1 WHERE email = %s AND senha = %s", (email, senha))
            conta = cursor.fetchone()
            cursor.fetchall()  # Lê todos os resultados restantes para evitar "Unread result found"
            cursor.close()
            conn.close()
            if conta:
                session['email'] = email
                return redirect(url_for('conta', numero=conta[0]))
            else:
                mensagem = "Login falhou. Email ou senha incorretos."
                return render_template('login.html', mensagem=mensagem)
        else:
            return "Erro ao conectar ao banco de dados"
    return render_template('login.html')

@app.route('/criar_conta', methods=['POST'])
def criar_conta():
    titular = request.form['titular']
    email = request.form['email']
    senha = request.form['senha']
    senha_hash = generate_password_hash(senha)

    conn = conectar_mysql()
    if conn:
        cursor = conn.cursor()
        numero = gerar_numero_conta()
        cursor.execute(
            "INSERT INTO Banco1 (numero_da_conta, titular, email, senha) VALUES (%s, %s, %s, %s)",
            (numero, titular, email, senha_hash)
        )
        conn.commit()
        cursor.close()
        return redirect(url_for('conta', numero=numero))
    else:
        return "Erro ao conectar ao banco de dados"

@app.route('/conta/<numero>')
def conta(numero):
    conn = conectar_mysql()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT numero_da_conta, titular, email, saldo FROM Banco1 WHERE numero_da_conta = %s", (numero,))
        conta = cursor.fetchone()
        cursor.close()
        conn.close()

        if conta:
            numero_da_conta, titular, email, saldo = conta
            saldo_atual = calcular_saldo_atual(numero)
            mensagem = request.args.get('mensagem')

            return render_template('conta.html', numero_da_conta=numero_da_conta, titular=titular, email=email, saldo_atual=saldo_atual, mensagem=mensagem)
        else:
            return f"Conta {numero} não encontrada."
    return "Erro ao conectar ao banco de dados"

def calcular_saldo_atual(numero):
    conn = conectar_mysql()
    if conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM Transacoes WHERE numero_da_conta = %s AND tipo_transacao = 'deposito'", (numero,))
        depositos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM Transacoes WHERE numero_da_conta = %s AND tipo_transacao = 'saque'", (numero,))
        saques = cursor.fetchone()[0]

        saldo_atual = depositos - saques

        cursor.close()
        conn.close()
        return saldo_atual
    else:
        return "Erro ao conectar ao banco de dados"

@app.route('/realizar_deposito/<numero>', methods=['POST'])
def realizar_deposito(numero):
    if 'email' not in session:
        return redirect(url_for('login'))
    valor = float(request.form['valor'])

    conn = conectar_mysql()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Banco1 SET saldo = saldo + %s WHERE numero_da_conta = %s", (valor, numero))
        cursor.execute("INSERT INTO Transacoes (numero_da_conta, tipo_transacao, valor) VALUES (%s, %s, %s)", (numero, 'deposito', valor))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('conta', numero=numero))
    else:
        return "Erro ao conectar ao banco de dados"

@app.route('/realizar_saque/<numero>', methods=['POST'])
def realizar_saque(numero):
    valor = float(request.form['valor'])

    conn = conectar_mysql()
    if conn:
        cursor = conn.cursor()

        cursor.execute("SELECT titular FROM Banco1 WHERE numero_da_conta = %s", (numero,))
        titular = cursor.fetchone()[0]

        saldo_atual = calcular_saldo_atual(numero)

        if valor > saldo_atual:
            mensagem = "Saldo insuficiente para realizar o saque."
            return redirect(url_for('conta', numero=numero, mensagem=mensagem))

        cursor.execute("UPDATE Banco1 SET saldo = saldo - %s WHERE numero_da_conta = %s", (valor, numero))
        cursor.execute("INSERT INTO Transacoes (numero_da_conta, tipo_transacao, valor) VALUES (%s, %s, %s)", (numero, 'saque', valor))
        conn.commit()
        
        mensagem = f"Saque de R$ {valor:.2f} realizado com sucesso."
        
        cursor.close()
        conn.close()

        return redirect(url_for('conta', numero=numero, mensagem=mensagem))
    else:
        return "Erro ao conectar ao banco de dados"

@app.route('/extrato/<numero>', methods=['GET'])
def extrato(numero):
    if 'email' not in session:
        return redirect(url_for('login'))
    conn = conectar_mysql()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Transacoes WHERE numero_da_conta = %s", (numero,))
        transacoes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('extrato.html', transacoes=transacoes)
    else:
        return "Erro ao conectar ao banco de dados"

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
