# APP/database.py
import sqlite3
from APP.config import DB_NAME
from APP.models import hash_password

def conectar():
    """Cria conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria as tabelas e o admin padrão."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            acao TEXT,
            data TEXT
        )
    """)

    # Cria o administrador padrão, se não existir
    cursor.execute("SELECT id FROM usuarios WHERE username = 'admin_master'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin_master", hash_password("admin123"), "admin")
        )

    conn.commit()
    conn.close()
