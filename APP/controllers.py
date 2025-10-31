# APP/controllers.py
from APP.models import User, listar_logs
from tkinter import messagebox

class UserController:
    """Camada intermediária entre a interface e o banco de dados."""

    @staticmethod
    def autenticar_usuario(username: str, password: str):
        if not username or not password:
            messagebox.showwarning("Aviso", "Preencha usuário e senha.")
            return False, None

        ok, role = User.autenticar(username, password)
        if not ok:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        return ok, role

    @staticmethod
    def criar_usuario(username: str, password: str, confirmar: str = None):
        if not username or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        if confirmar and password != confirmar:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return

        try:
            User.registrar(username, password)
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    @staticmethod
    def excluir_usuario(username: str, executor: str):
        try:
            User.excluir_usuario(username, executor)
            messagebox.showinfo("Sucesso", f"Usuário '{username}' excluído.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    @staticmethod
    def alterar_role(username: str, novo_role: str):
        try:
            User.alterar_role(username, novo_role)
            messagebox.showinfo("Sucesso", f"Papel de '{username}' alterado para {novo_role}.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    @staticmethod
    def obter_lista_usuarios():
        return User.listar_usuarios()

    @staticmethod
    def obter_logs():
        return listar_logs()
