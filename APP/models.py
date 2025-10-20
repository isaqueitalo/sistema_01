import sqlite3
import hashlib
from APP.database import conectar

class User:
    """Classe para gerenciar usuários (registro e autenticação)."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Criptografa a senha com SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def registrar(username: str, password: str):
        """Registra um novo usuário no banco."""
        conn = conectar()
        cursor = conn.cursor()
        try:
            password_hash = User.hash_password(password)
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Usuário já existe!")
        finally:
            conn.close()

    @staticmethod
    def autenticar(username: str, password: str) -> bool:
        """Valida o login."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and User.hash_password(password) == result[0]:
            return True
        return False

