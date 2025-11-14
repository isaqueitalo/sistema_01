# APP/core/migrations.py
"""
Gerenciador simples de migrações para SQLite usando PRAGMA user_version.

Como funciona:
- Cada função de migração em MIGRATIONS aplica mudanças no schema (sem perder dados).
- O número da migração é a sua posição (1-based) na lista MIGRATIONS.
- Quando run_migrations() é chamado, ele lê user_version atual e aplica
  todas as migrações necessárias, atualizando PRAGMA user_version ao final de cada uma.

Exemplo de uso:
    from APP.core.migrations import run_migrations
    run_migrations()
"""

from typing import Callable, List
from APP.core.database import conectar, DEFAULT_CATEGORIES, DEFAULT_UNITS
from APP.core.logger import logger
import sqlite3

# Cada migração é uma função conn -> None
def _migration_001_create_missing_role_column(conn: sqlite3.Connection):
    """
    Migração 1:
    Garante que a coluna 'role' exista na tabela usuarios.
    (Se a tabela for gerada por outro script, pode não ter a coluna; essa migração adiciona com default.)
    """
    cur = conn.cursor()
    # verifica existência da coluna
    cur.execute("PRAGMA table_info(usuarios)")
    cols = [r[1] for r in cur.fetchall()]
    if "role" not in cols:
        logger.info("Migração 001: adicionando coluna 'role' na tabela usuarios.")
        cur.execute("ALTER TABLE usuarios ADD COLUMN role TEXT NOT NULL DEFAULT 'vendedor'")
        conn.commit()
    else:
        logger.debug("Migração 001: coluna 'role' já existe — pulando.")


def _migration_002_add_vendedor_to_vendas(conn: sqlite3.Connection):
    """
    Migração 2:
    Adiciona coluna 'vendedor' em tabela 'vendas' (se não existir).
    """
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vendas)")
    cols = [r[1] for r in cur.fetchall()]
    if "vendedor" not in cols:
        logger.info("Migração 002: adicionando coluna 'vendedor' na tabela vendas.")
        cur.execute("ALTER TABLE vendas ADD COLUMN vendedor TEXT")
        conn.commit()
    else:
        logger.debug("Migração 002: coluna 'vendedor' já existe — pulando.")


def _migration_003_create_migrations_table(conn: sqlite3.Connection):
    """
    Migração 3:
    (opcional) cria tabela de controle de migrações — usada apenas para histórico, não é obrigatória.
    """
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS migrations_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration INTEGER NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def _migration_004_create_catalog_tables(conn: sqlite3.Connection):
    """
    Migração 4:
    Cria tabelas auxiliares de categorias e unidades de medida e preenche com valores padrão.
    """
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            segmento TEXT DEFAULT 'geral'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS unidades_medida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla TEXT UNIQUE NOT NULL,
            descricao TEXT
        )
    """)
    cur.executemany(
        "INSERT OR IGNORE INTO categorias (nome, segmento) VALUES (?, ?)",
        DEFAULT_CATEGORIES,
    )
    cur.executemany(
        "INSERT OR IGNORE INTO unidades_medida (sigla, descricao) VALUES (?, ?)",
        DEFAULT_UNITS,
    )
    conn.commit()


def _migration_005_extend_produtos_schema(conn: sqlite3.Connection):
    """
    Migração 5:
    Adiciona colunas extras à tabela de produtos para suportar segmentos diferentes.
    """
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(produtos)")
    cols = {row[1] for row in cur.fetchall()}

    additions = [
        ("categoria_id", "INTEGER"),
        ("unidade_id", "INTEGER"),
        ("codigo_barras", "TEXT"),
        ("estoque_minimo", "INTEGER DEFAULT 0"),
        ("localizacao", "TEXT"),
    ]

    for col_name, col_def in additions:
        if col_name not in cols:
            logger.info(f"Migração 005: adicionando coluna '{col_name}' à tabela produtos.")
            cur.execute(f"ALTER TABLE produtos ADD COLUMN {col_name} {col_def}")
    conn.commit()


def _migration_006_expand_vendas_table(conn: sqlite3.Connection):
    """
    Migração 6:
    Adiciona colunas de cliente e forma de pagamento à tabela de vendas.
    """
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vendas)")
    cols = {row[1] for row in cur.fetchall()}

    if "cliente" not in cols:
        logger.info("Migração 006: adicionando coluna 'cliente' na tabela vendas.")
        cur.execute("ALTER TABLE vendas ADD COLUMN cliente TEXT")

    if "forma_pagamento" not in cols:
        logger.info("Migração 006: adicionando coluna 'forma_pagamento' na tabela vendas.")
        cur.execute("ALTER TABLE vendas ADD COLUMN forma_pagamento TEXT")

    conn.commit()


def _migration_007_add_pedido_id_to_vendas(conn: sqlite3.Connection):
    """
    Migração 7:
    Adiciona coluna 'pedido_id' para rastrear vendas completas.
    """
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vendas)")
    cols = {row[1] for row in cur.fetchall()}
    if "pedido_id" not in cols:
        logger.info("Migração 007: adicionando coluna 'pedido_id' na tabela vendas.")
        cur.execute("ALTER TABLE vendas ADD COLUMN pedido_id TEXT")
        conn.commit()
    else:
        logger.debug("Migração 007: coluna 'pedido_id' já existe - pulando.")


# Lista ordenada de migrações (adicionar novas funções ao final)
MIGRATIONS: List[Callable[[sqlite3.Connection], None]] = [
    _migration_001_create_missing_role_column,
    _migration_002_add_vendedor_to_vendas,
    _migration_003_create_migrations_table,
    _migration_004_create_catalog_tables,
    _migration_005_extend_produtos_schema,
    _migration_006_expand_vendas_table,
    _migration_007_add_pedido_id_to_vendas,
]


def _get_user_version(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("PRAGMA user_version")
    return cur.fetchone()[0]


def _set_user_version(conn: sqlite3.Connection, version: int):
    cur = conn.cursor()
    cur.execute(f"PRAGMA user_version = {version}")
    conn.commit()


def run_migrations():
    """
    Executa as migrações pendentes.
    - Lê PRAGMA user_version (versão atual).
    - Para cada migração com índice > user_version aplica e incrementa o user_version.
    """
    logger.info("Verificando migrações do banco de dados...")
    try:
        conn = conectar()
        current = _get_user_version(conn)
        logger.info(f"Versão atual do schema: {current}. {len(MIGRATIONS)} migrações disponíveis.")

        total = len(MIGRATIONS)
        # migrações são 1-based
        for idx, migration in enumerate(MIGRATIONS, start=1):
            if idx > current:
                logger.info(f"Aplicando migração {idx}/{total} -> {migration.__name__}")
                try:
                    migration(conn)
                    _set_user_version(conn, idx)
                    # registra histórico se a tabela existir
                    try:
                        cur = conn.cursor()
                        cur.execute("INSERT INTO migrations_history (migration) VALUES (?)", (idx,))
                        conn.commit()
                    except Exception:
                        # se não existir a tabela de histórico, ignora (foi criada numa migração posterior possivelmente)
                        pass
                    logger.info(f"Migração {idx} aplicada com sucesso.")
                except Exception as e:
                    logger.error(f"Falha ao aplicar migração {idx}: {e}", exc_info=True)
                    raise
            else:
                logger.debug(f"Migração {idx} já aplicada, pulando.")
        conn.close()
        logger.info("Verificação de migrações finalizada.")
    except Exception as e:
        logger.critical(f"Erro ao executar migrações: {e}", exc_info=True)
        raise


def ensure_run_migrations_safe():
    """
    Chamar no startup depois de inicializar a conexão.
    Exemplos:
        inicializar_banco()
        run_migrations()
    """
    run_migrations()
