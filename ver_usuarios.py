# ver_usuarios.py
import sqlite3

DB_PATH = "DATA/usuarios.db"

def listar_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    if not usuarios:
        print("Nenhum usuário encontrado.")
    else:
        print("=== Usuários cadastrados ===")
        for user in usuarios:
            print(f"ID: {user[0]} | Nome: {user[1]}")

if __name__ == "__main__":
    listar_usuarios()
