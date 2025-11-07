import sqlite3
from APP.config import DB_NAME
from APP.utils import hash_password
from APP.logger import logger  # ✅ Importa o logger centralizado

def inicializar_banco():
    """Cria o banco e as tabelas se ainda não existirem."""
    try:
        logger.info("Inicializando o banco de dados...")
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
        logger.debug("Tabela 'usuarios' verificada/criada com sucesso.")
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
        logger.debug("Tabela 'logs' verificada/criada com sucesso.")
        conn.commit()

            # === TABELA DE VENDAS ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                vendedor TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                total REAL NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
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
            logger.info("Usuário 'admin_master' criado com sucesso.")
        else:
            logger.info("Usuário 'admin_master' já existe. Nenhuma alteração necessária.")

    except sqlite3.Error as e:
        logger.error(f"Erro no SQLite durante inicialização do banco: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"Erro inesperado ao inicializar o banco: {e}", exc_info=True)
    finally:
        try:
            conn.close()
            logger.debug("Conexão com o banco encerrada.")
        except Exception:
            logger.warning("Falha ao encerrar a conexão com o banco.", exc_info=True)


def conectar():
    """Abre uma conexão com o banco."""
    try:
        conn = sqlite3.connect(DB_NAME)
        logger.debug("Conexão aberta com o banco de dados.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}", exc_info=True)
        raise  # Repassa o erro para quem chamou, se necessário
