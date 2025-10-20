# APP/database.py
import sqlite3
from APP.config import DB_NAME

def inicializar_banco():
    """Cria o banco e a tabela de usuários se ainda não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def conectar():
    """Abre uma conexão com o banco."""
    return sqlite3.connect(DB_NAME)
