import sqlite3
import os

def conectar():

    #print("BANCO SENDO CRIADO EM:", os.getcwd())

    caminho_db = os.path.join(os.path.dirname(__file__), "motorista.db")


    conn = sqlite3.connect(caminho_db, check_same_thread=False)
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS corridas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT,
        motorista TEXT,
        data TEXT,
        tipo_pagamento TEXT,
        km REAL,
        corridas INTEGER,
        valor REAL,
        gasolina REAL,
        despesas_extras REAL,
        valor_km REAL,
        taxa REAL,
        lucro REAL
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT UNIQUE,
            senha TEXT,
            liberado INTEGER DEFAULT 0,
            trocar_senha INTEGER DEFAULT 1
        )
        """)

    conn.commit()

    return conn, cursor

print(os.getcwd())