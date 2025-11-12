# APP/core/database.py
import sqlite3
import os
from datetime import datetime
from APP.core.config import config
from APP.core.logger import logger
from APP.core.utils import hash_password

DEFAULT_CATEGORIES = [
    ("Geral", "geral"),
    ("Medicamentos", "farmacia"),
    ("Higiene pessoal", "farmacia"),
    ("Padaria", "padaria"),
    ("Bebidas", "padaria"),
]

DEFAULT_UNITS = [
    ("UN", "Unidade"),
    ("CX", "Caixa"),
    ("KG", "Quilograma"),
    ("G", "Gramas"),
    ("L", "Litro"),
    ("ML", "Mililitro"),
]


# ============================================================
# CONEXÃO AO BANCO
# ============================================================
def conectar():
    """Retorna uma conexão SQLite ativa."""
    try:
        conn = sqlite3.connect(config.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn
    except Exception as e:
        logger.critical(f"Erro ao conectar ao banco de dados: {e}", exc_info=True)
        raise


# ============================================================
# INICIALIZAÇÃO DO BANCO
# ============================================================
def inicializar_banco():
    """Cria tabelas e garante a existência do admin_master."""
    logger.info("Inicializando o banco de dados...")
    conn = conectar()
    cur = conn.cursor()

    # --------------------------------------------------------
    # TABELA DE USUÁRIOS (3 ROLES: admin_master, admin, vendedor)
    # --------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin_master', 'admin', 'vendedor')) NOT NULL DEFAULT 'vendedor'
        )
    """)

    # --------------------------------------------------------
    # TABELA DE LOGS
    # --------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            acao TEXT NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # TABELA DE PRODUTOS
    # --------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0,
            fornecedor TEXT,
            validade DATE,
            categoria_id INTEGER,
            unidade_id INTEGER,
            codigo_barras TEXT,
            estoque_minimo INTEGER DEFAULT 0,
            localizacao TEXT,
            FOREIGN KEY(categoria_id) REFERENCES categorias(id),
            FOREIGN KEY(unidade_id) REFERENCES unidades_medida(id)
        )
    """)

    # --------------------------------------------------------
    # TABELA DE CATEGORIAS
    # --------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            segmento TEXT DEFAULT 'geral'
        )
    """)

    # --------------------------------------------------------
    # TABELA DE UNIDADES DE MEDIDA
    # --------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS unidades_medida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla TEXT UNIQUE NOT NULL,
            descricao TEXT
        )
    """)

    _seed_default_catalogs(cur)

    # --------------------------------------------------------
    # TABELA DE VENDAS
    # --------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            total REAL NOT NULL,
            vendedor TEXT,
            cliente TEXT,
            forma_pagamento TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # --------------------------------------------------------
    # GARANTIR ADMIN MASTER E USUÁRIOS PADRÃO DO config.json
    # --------------------------------------------------------
    from APP.core.config import config

    cur.execute("SELECT COUNT(*) as total FROM usuarios")
    total = cur.fetchone()["total"]

    if total == 0:
        usuarios_padrao = config.default_users

        for u in usuarios_padrao:
            nome = u["username"]
            senha_hash = hash_password(u["password"])
            role = u["role"]
            cur.execute(
                "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                (nome, senha_hash, role),
            )
            logger.info(f"✅ Usuário padrão criado: {nome} ({role})")

        conn.commit()
        logger.info("✅ Usuários padrão criados com sucesso.")
    else:
        logger.info("✅ Usuários já existentes — nenhuma alteração feita.")

    conn.close()
    logger.info("Banco de dados inicializado com sucesso.")


def _seed_default_catalogs(cur):
    """Garante catálogos básicos para segmentos atendidos pelo sistema."""
    cur.executemany(
        "INSERT OR IGNORE INTO categorias (nome, segmento) VALUES (?, ?)",
        DEFAULT_CATEGORIES,
    )
    cur.executemany(
        "INSERT OR IGNORE INTO unidades_medida (sigla, descricao) VALUES (?, ?)",
        DEFAULT_UNITS,
    )


# ============================================================
# BACKUP DO BANCO DE DADOS
# ============================================================
def criar_backup():
    """Cria uma cópia de segurança do banco de dados na pasta /DATA/backups."""
    try:
        backup_dir = os.path.join(os.path.dirname(config.db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join(backup_dir, backup_name)

        with open(config.db_path, "rb") as original, open(backup_path, "wb") as copia:
            copia.write(original.read())

        logger.info(f"💾 Backup criado com sucesso: {backup_path}")
        return backup_path

    except Exception as e:
        logger.error(f"Erro ao criar backup do banco: {e}", exc_info=True)
        return None
