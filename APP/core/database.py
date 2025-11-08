import sqlite3
from APP.core.config import DB_NAME
from APP.core.logger import logger
from APP.core.utils import hash_password


def conectar():
    return sqlite3.connect(DB_NAME)


def inicializar_banco():
    logger.info("Inicializando o banco de dados...")
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            acao TEXT NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            total REAL NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    cur.execute("SELECT * FROM usuarios WHERE username='admin_master'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin_master", hash_password("Admin@123"), "admin")
        )
        conn.commit()
        logger.info("Usuário admin_master criado com sucesso.")
    else:
        logger.info("Usuário 'admin_master' já existe. Nenhuma alteração necessária.")

    conn.close()
    logger.info("Banco de dados inicializado com sucesso.")
