from APP.core.database import conectar
from APP.core.utils import hash_password, check_password
from APP.core.logger import logger


class User:
    """Modelo de Usuários — autenticação, permissões e segurança com 3 níveis."""

    # ============================================================
    # AUTENTICAÇÃO
    # ============================================================
    @staticmethod
    def autenticar(username, password):
        """Verifica credenciais e retorna (True, role) se válidas."""
        conn = conectar()
        cur = conn.cursor()

        cur.execute("SELECT password_hash, role FROM usuarios WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()

        if not row:
            logger.warning(f"Tentativa de login com usuário inexistente: '{username}'.")
            return False, None

        senha_hash, role = row
        if check_password(password, senha_hash):
            logger.info(f"Usuário '{username}' autenticado com sucesso ({role}).")
            return True, role
        else:
            logger.warning(f"Tentativa de login inválida: {username}")
            return False, None

    # ============================================================
    # REGISTRO
    # ============================================================
    @staticmethod
    def registrar(username, password, role="vendedor"):
        """
        Cria um novo usuário.
        Roles válidos: 'admin_master', 'admin', 'vendedor'
        """
        roles_validos = ("admin_master", "admin", "vendedor")

        if role not in roles_validos:
            logger.error(f"Role inválida: {role}")
            raise ValueError(f"Tipo de usuário inválido! Use um dos seguintes: {roles_validos}")

        conn = conectar()
        cur = conn.cursor()

        # Verifica se o usuário já existe
        cur.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cur.fetchone():
            conn.close()
            logger.warning(f"Tentativa de criar usuário já existente: '{username}'.")
            raise ValueError("Usuário já existe!")

        # Garante que só exista um admin_master
        if role == "admin_master":
            cur.execute("SELECT id FROM usuarios WHERE role = 'admin_master'")
            if cur.fetchone():
                conn.close()
                logger.warning("Tentativa de criar outro admin_master bloqueada.")
                raise PermissionError("Já existe um admin_master cadastrado!")

        cur.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        conn.close()

        logger.info(f"Usuário '{username}' criado com sucesso (função: {role}).")

    # ============================================================
    # LISTAGEM
    # ============================================================
    @staticmethod
    def listar():
        """Retorna todos os usuários cadastrados."""
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM usuarios ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        logger.debug(f"{len(rows)} usuários listados.")
        return rows

    # ============================================================
    # EXCLUSÃO
    # ============================================================
    @staticmethod
    def excluir(nome_alvo, usuario_logado):
        """
        Exclui um usuário, com segurança:
        - 'admin_master' não pode ser excluído.
        - O usuário logado não pode se autoexcluir.
        """
        if nome_alvo == "admin_master":
            logger.warning("Tentativa de excluir 'admin_master' bloqueada.")
            raise PermissionError("O usuário 'admin_master' não pode ser excluído!")

        if nome_alvo == usuario_logado:
            logger.warning(f"O usuário '{usuario_logado}' tentou se autoexcluir.")
            raise PermissionError("Você não pode excluir a si mesmo!")

        conn = conectar()
        cur = conn.cursor()

        cur.execute("SELECT id FROM usuarios WHERE username = ?", (nome_alvo,))
        if not cur.fetchone():
            conn.close()
            logger.warning(f"Tentativa de excluir usuário inexistente: '{nome_alvo}'.")
            raise ValueError("Usuário não encontrado!")

        cur.execute("DELETE FROM usuarios WHERE username = ?", (nome_alvo,))
        conn.commit()
        conn.close()

        logger.info(f"Usuário '{nome_alvo}' excluído por '{usuario_logado}'.")

    # ============================================================
    # GARANTIA DE ADMIN PADRÃO
    # ============================================================
    @staticmethod
    def garantir_admin_padrao():
        """Garante que 'admin_master' exista no banco de dados."""
        conn = conectar()
        cur = conn.cursor()

        cur.execute("SELECT id FROM usuarios WHERE username = 'admin_master'")
        if not cur.fetchone():
            senha_hash = hash_password("1234")
            cur.execute(
                "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin_master", senha_hash, "admin_master"),
            )
            conn.commit()
            logger.info("Usuário 'admin_master' criado automaticamente (senha padrão: 1234).")
        else:
            logger.debug("Usuário 'admin_master' já existe.")

        conn.close()
