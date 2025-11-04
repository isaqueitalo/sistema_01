import sqlite3
from APP.config import DB_NAME
from APP.utils import hash_password 

def inicializar_banco():
    """Cria o banco e as tabelas se ainda não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # === TABELA DE USUÁRIOS ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    conn.commit()

    # === TABELA DE LOGS ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            acao TEXT NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # === INSERE O ADMIN MASTER SE NÃO EXISTIR ===
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin_master'")
    if not cursor.fetchone():
        admin_pass = hash_password("Admin@123") 
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin_master", admin_pass, "admin")
        )
        conn.commit()

    conn.close()


def conectar():
    """Abre uma conexão com o banco."""
    return sqlite3.connect(DB_NAME)
