import sqlite3

"""
conn = sqlite3.connect("motorista.db")
cursor = conn.cursor()

cpf = "10808560646"
nova_senha = "108085"

cursor.execute(
    "UPDATE usuarios SET senha=? WHERE cpf=?",
    (nova_senha, cpf)
)

conn.commit()

print("Senha alterada com sucesso")

"""

conn = sqlite3.connect("motorista.db")
cursor = conn.cursor()

usuarios = cursor.execute("SELECT * FROM usuarios").fetchall()

for u in usuarios:
    print(u)