import sqlite3
from datetime import datetime
from APP.database import conectar 
from APP.config import DB_NAME
from APP.utils import hash_password


class Log:
    """Classe para registrar e listar logs de atividades."""

    @staticmethod
    def registrar(usuario: str, acao: str):
        """Grava ações no log de atividades."""
        conn = conectar()
        cursor = conn.cursor()

        # 🚨 Alinha o nome da coluna com o database.py
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO logs (usuario, acao, data_hora) VALUES (?, ?, ?)",
            (usuario, acao, agora)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def listar():
        """Retorna os registros de log (para exibir na interface)."""
        conn = conectar()
        cursor = conn.cursor()

        # Garante que a tabela exista
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                acao TEXT NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("SELECT usuario, acao, data_hora FROM logs ORDER BY id DESC")
        logs = cursor.fetchall()
        conn.close()
        return logs



class User:
    """Gerencia CRUD de usuários e autenticação."""

    @staticmethod
    def autenticar(username: str, password: str):
        """Autentica usuário no banco e retorna (True, role) se válido."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash, role FROM usuarios WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            return False, None

        senha_hash, role = result
        if senha_hash == hash_password(password):
            Log.registrar(username, "login_sucesso")
            return True, role
        else:
            Log.registrar(username, "login_falhou")
            return False, None

    @staticmethod
    def registrar(username: str, password: str, role: str = "user"):
        """Registra um novo usuário."""
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            raise Exception("Usuário já existe!")

        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        conn.close()

        Log.registrar(username, f"usuario_criado ({role})")

    @staticmethod
    def listar_usuarios():
        """Retorna lista com (id, username, role)."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM usuarios ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def excluir_usuario(username: str, executor: str):
        """Exclui um usuário — não permite excluir o administrador."""
        if username == "admin_master":
            raise Exception("O usuário administrador não pode ser excluído!")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        if cursor.rowcount == 0:
            conn.close()
            raise Exception("Usuário não encontrado.")
        conn.commit()
        conn.close()

        Log.registrar(executor, f"excluiu_usuario({username})")

    @staticmethod
    def alterar_role(username: str, novo_role: str):
        """Altera o papel de um usuário (user/admin)."""
        if username == "admin_master":
            raise Exception("O papel do administrador não pode ser alterado!")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET role = ? WHERE username = ?", (novo_role, username))
        if cursor.rowcount == 0:
            conn.close()
            raise Exception("Usuário não encontrado.")
        conn.commit()
        conn.close()

        Log.registrar(username, f"alterou_role_para({novo_role})")
