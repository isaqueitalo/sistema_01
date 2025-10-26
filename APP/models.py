# APP/models.py
import sqlite3
import hashlib
from APP.database import conectar
from APP.utils import senha_valida

class User:
    """Classe para gerenciar usuários (registro, autenticação e administração)."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @staticmethod
    def hash_password(password: str) -> str:
        """Criptografa a senha com SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def registrar(username: str, password: str, role="user"):
        """Registra um novo usuário no banco."""
        if not senha_valida(password):
            raise ValueError("A senha não atende aos requisitos mínimos.")
        conn = conectar()
        cursor = conn.cursor()
        try:
            password_hash = User.hash_password(password)
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Usuário já existe!")
        finally:
            conn.close()

    @staticmethod
    def autenticar(username: str, password: str) -> tuple[bool, str]:
        """Valida o login e retorna (True/False, role)."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, role FROM usuarios WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and User.hash_password(password) == result[0]:
            return True, result[1]  # Retorna o papel (role)
        return False, None

    @staticmethod
    def editar_senha(username: str, nova_senha: str):
        """Atualiza a senha de um usuário."""
        if not senha_valida(nova_senha):
            raise ValueError("A nova senha não atende aos requisitos mínimos.")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET password_hash = ? WHERE username = ?",
            (User.hash_password(nova_senha), username)
        )
        if cursor.rowcount == 0:
            raise ValueError("Usuário não encontrado.")
        conn.commit()
        conn.close()

    @staticmethod
    def excluir_usuario(username: str):
        """Exclui um usuário, exceto o administrador."""
        if username == "admin_master":
            raise PermissionError("O usuário administrador não pode ser excluído.")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        if cursor.rowcount == 0:
            raise ValueError("Usuário não encontrado.")
        conn.commit()
        conn.close()

    @staticmethod
    def listar_usuarios():
        """Retorna uma lista com todos os usuários e seus papéis."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM usuarios ORDER BY role DESC")
        data = cursor.fetchall()
        conn.close()
        return data
