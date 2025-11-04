# APP/controllers.py
from APP.models.usuarios_models import User, Log

class UserController:
    """Camada intermediária entre a interface e o banco de dados."""

    # === AUTENTICAÇÃO ===
    @staticmethod
    def autenticar_usuario(username: str, password: str):
        """Valida login e retorna (ok, role, mensagem)."""
        if not username or not password:
            return False, None, "Preencha usuário e senha."

        ok, role = User.autenticar(username, password)
        if not ok:
            return False, None, "Usuário ou senha incorretos."

        return True, role, f"Bem-vindo, {username}!"

    # === CADASTRO DE USUÁRIOS ===
    @staticmethod
    def criar_usuario(username: str, password: str, confirmar: str = None):
        """Cria novo usuário, com validações."""
        if not username or not password:
            return False, "Preencha todos os campos."

        if confirmar and password != confirmar:
            return False, "As senhas não coincidem."

        try:
            User.registrar(username, password)
            return True, "Usuário criado com sucesso!"
        except Exception as e:
            return False, str(e)

    # === EXCLUSÃO DE USUÁRIOS ===
    @staticmethod
    def excluir_usuario(username: str, executor: str):
        """Exclui um usuário existente."""
        try:
            User.excluir_usuario(username, executor)
            return True, f"Usuário '{username}' excluído com sucesso."
        except Exception as e:
            return False, str(e)

    # === ALTERAÇÃO DE PAPEL ===
    @staticmethod
    def alterar_role(username: str, novo_role: str):
        """Muda o papel de um usuário."""
        try:
            User.alterar_role(username, novo_role)
            return True, f"Papel de '{username}' alterado para {novo_role}."
        except Exception as e:
            return False, str(e)

    # === LISTAGENS ===
    @staticmethod
    def obter_lista_usuarios():
        """Retorna a lista de usuários (id, username, role)."""
        return User.listar_usuarios()

    @staticmethod
    def obter_logs():
        """Retorna a lista de logs."""
        return Log.listar()
