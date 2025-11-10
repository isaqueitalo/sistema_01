# APP/core/resetar_banco.py
import os
from APP.core.database import conectar
from APP.core.utils import hash_password
from APP.core.logger import logger


def resetar_banco_usuarios():
    """Recria a tabela de usuários e insere usuários padrão com hierarquia de papéis."""
    try:
        conn = conectar()
        cur = conn.cursor()

        # Descobre o caminho real do banco (útil para depuração)
        try:
            db_path = cur.execute("PRAGMA database_list;").fetchone()[2]
        except Exception:
            db_path = "(desconhecido)"

        print(f"📁 Usando banco de dados: {db_path}")
        logger.info(f"🔄 Resetando tabela de usuários no banco: {db_path}")

        # Remove a tabela antiga se existir
        cur.execute("DROP TABLE IF EXISTS usuarios")

        # Cria novamente a tabela com estrutura limpa
        cur.execute("""
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)

        # === Usuários padrão com funções distintas ===
        usuarios_padrao = [
            ("admin_master", "Master@123", "admin_master"),  # superusuário
            ("admin", "Admin@123", "admin"),                 # administrador comum
            ("vendedor1", "Vendedor@123", "vendedor"),       # vendedor comum
        ]

        for nome, senha, role in usuarios_padrao:
            senha_hash = hash_password(senha)
            cur.execute(
                "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                (nome, senha_hash, role),
            )
            logger.info(f"✅ Usuário criado: {nome} ({role})")

        conn.commit()

        # Exibe os usuários para confirmação
        cur.execute("SELECT id, username, role FROM usuarios ORDER BY id")
        usuarios = cur.fetchall()
        conn.close()

        print("\n=== Usuários cadastrados ===")
        for u in usuarios:
            print(f"👤 ID: {u[0]} | Usuário: {u[1]} | Função: {u[2]}")
        print("============================\n")

        logger.info("🏁 Reset de usuários concluído com sucesso!")
        print("✅ Banco e usuários padrão criados com sucesso!")

    except Exception as e:
        logger.error(f"❌ Erro ao resetar banco de usuários: {e}", exc_info=True)
        print(f"Erro: {e}")


if __name__ == "__main__":
    resetar_banco_usuarios()
