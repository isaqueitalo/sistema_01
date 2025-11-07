import sqlite3
from datetime import datetime
from APP.database import conectar
from APP.config import DB_NAME
from APP.utils import hash_password
from APP.logger import logger  # ✅ Importa o logger centralizado


class Log:
    """Classe para registrar e listar logs de atividades (auditoria)."""

    @staticmethod
    def registrar(usuario: str, acao: str):
        """Grava ações no log de atividades (tabela SQLite)."""
        try:
            conn = conectar()
            cursor = conn.cursor()

            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO logs (usuario, acao, data_hora) VALUES (?, ?, ?)",
                (usuario, acao, agora)
            )
            conn.commit()
            logger.debug(f"Log de ação registrado: {usuario} → {acao}")
        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao registrar log de ação: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Erro inesperado ao registrar log: {e}", exc_info=True)
        finally:
            try:
                conn.close()
            except Exception:
                logger.warning("Falha ao fechar conexão após registrar log.", exc_info=True)

    @staticmethod
    def listar():
        """Retorna os registros de log (para exibir na interface)."""
        try:
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
            logger.debug(f"{len(logs)} registros de log recuperados do banco.")
            return logs
        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao listar logs: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.critical(f"Erro inesperado ao listar logs: {e}", exc_info=True)
            return []
        finally:
            try:
                conn.close()
            except Exception:
                logger.warning("Falha ao fechar conexão após listar logs.", exc_info=True)


class User:
    """Gerencia CRUD de usuários e autenticação."""

    @staticmethod
    def autenticar(username: str, password: str):
        """Autentica usuário no banco e retorna (True, role) se válido."""
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash, role FROM usuarios WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                logger.warning(f"Tentativa de login com usuário inexistente: '{username}'.")
                return False, None

            senha_hash, role = result
            if senha_hash == hash_password(password):
                Log.registrar(username, "login_sucesso")
                logger.info(f"Usuário '{username}' autenticado com sucesso.")
                return True, role
            else:
                Log.registrar(username, "login_falhou")
                logger.warning(f"Usuário '{username}' falhou na autenticação (senha incorreta).")
                return False, None

        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao autenticar '{username}': {e}", exc_info=True)
            return False, None
        except Exception as e:
            logger.critical(f"Erro inesperado ao autenticar '{username}': {e}", exc_info=True)
            return False, None

    @staticmethod
    def registrar(username: str, password: str, role: str = "user"):
        """Registra um novo usuário."""
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
            if cursor.fetchone():
                logger.warning(f"Tentativa de criação de usuário duplicado: '{username}'.")
                conn.close()
                raise Exception("Usuário já existe!")

            cursor.execute(
                "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role)
            )
            conn.commit()
            conn.close()

            Log.registrar(username, f"usuario_criado ({role})")
            logger.info(f"Novo usuário '{username}' criado com sucesso (role={role}).")

        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao registrar usuário '{username}': {e}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Erro inesperado ao registrar usuário '{username}': {e}", exc_info=True)
            raise
        finally:
            try:
                conn.close()
            except Exception:
                logger.warning("Falha ao fechar conexão após registrar usuário.", exc_info=True)

    @staticmethod
    def listar_usuarios():
        """Retorna lista com (id, username, role)."""
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM usuarios ORDER BY id ASC")
            rows = cursor.fetchall()
            logger.debug(f"{len(rows)} usuários listados.")
            return rows
        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao listar usuários: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.critical(f"Erro inesperado ao listar usuários: {e}", exc_info=True)
            return []
        finally:
            try:
                conn.close()
            except Exception:
                logger.warning("Falha ao fechar conexão após listar usuários.", exc_info=True)

    @staticmethod
    def excluir_usuario(username: str, executor: str):
        """Exclui um usuário — não permite excluir o administrador."""
        try:
            if username == "admin_master":
                logger.warning("Tentativa de excluir o usuário 'admin_master'.")
                raise Exception("O usuário administrador não pode ser excluído!")

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
            if cursor.rowcount == 0:
                logger.warning(f"Tentativa de exclusão de usuário inexistente: '{username}'.")
                conn.close()
                raise Exception("Usuário não encontrado.")
            conn.commit()
            conn.close()

            Log.registrar(executor, f"excluiu_usuario({username})")
            logger.info(f"Usuário '{username}' excluído por '{executor}'.")

        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao excluir usuário '{username}': {e}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Erro inesperado ao excluir usuário '{username}': {e}", exc_info=True)
            raise
        finally:
            try:
                conn.close()
            except Exception:
                logger.warning("Falha ao fechar conexão após excluir usuário.", exc_info=True)

    @staticmethod
    def alterar_role(username: str, novo_role: str):
        """Altera o papel de um usuário (user/admin)."""
        try:
            if username == "admin_master":
                logger.warning("Tentativa de alterar o papel do 'admin_master'.")
                raise Exception("O papel do administrador não pode ser alterado!")

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET role = ? WHERE username = ?", (novo_role, username))
            if cursor.rowcount == 0:
                logger.warning(f"Tentativa de alterar role de usuário inexistente: '{username}'.")
                conn.close()
                raise Exception("Usuário não encontrado.")
            conn.commit()
            conn.close()

            Log.registrar(username, f"alterou_role_para({novo_role})")
            logger.info(f"Usuário '{username}' teve role alterado para '{novo_role}'.")

        except sqlite3.Error as e:
            logger.error(f"Erro SQLite ao alterar role de '{username}': {e}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Erro inesperado ao alterar role de '{username}': {e}", exc_info=True)
            raise
        finally:
            try:
                conn.close()
            except Exception:
                logger.warning("Falha ao fechar conexão após alterar role.", exc_info=True)
