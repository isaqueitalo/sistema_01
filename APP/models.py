# APP/models.py
import sqlite3
import hashlib
from datetime import datetime
from APP.config import DB_NAME


def conectar():
    """Cria conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)


def hash_password(password: str) -> str:
    """Gera um hash SHA256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()


class User:
    # === CRUD e autenticação ===
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
            registrar_log(username, "login_sucesso")
            return True, role
        else:
            registrar_log(username, "login_falhou")
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

        registrar_log(username, f"usuario_criado ({role})")

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

        registrar_log(executor, f"excluiu_usuario({username})")

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

        registrar_log(username, f"alterou_role_para({novo_role})")


# === LOG DE ATIVIDADES ===
def registrar_log(usuario: str, acao: str):
    """Grava ações no log de atividades."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            acao TEXT,
            data TEXT
        )
    """)

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (usuario, acao, data) VALUES (?, ?, ?)",
                   (usuario, acao, agora))

    conn.commit()
    conn.close()


def listar_logs():
    """Retorna os registros de log (para uso futuro na interface)."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, acao, data FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs
