import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter.simpledialog import askstring
from APP.models.usuarios_models import User, Log
from APP.logger import logger


class UsuariosUI(tb.Frame):
    """Tela de gerenciamento de usuários (somente admin e admin_master)."""

    def __init__(self, master, user_logado: str, role: str):
        super().__init__(master)
        self.master = master
        self.user_logado = user_logado
        self.role = role
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 🔒 Permissão
        if self.role != "admin" and self.user_logado != "admin_master":
            messagebox.showwarning("Acesso negado", "Apenas administradores podem gerenciar usuários.")
            self.voltar_menu()
            return

        tb.Label(
            self,
            text="👥 Gerenciamento de Usuários",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 15))

        # === Botões principais ===
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(
            btn_frame,
            text="➕ Adicionar Usuário",
            bootstyle=SUCCESS,
            command=self.adicionar_usuario
        ).grid(row=0, column=0, padx=10)

        tb.Button(
            btn_frame,
            text="✏️ Alterar Papel (Role)",
            bootstyle=INFO,
            command=self.alterar_role
        ).grid(row=0, column=1, padx=10)

        tb.Button(
            btn_frame,
            text="❌ Excluir Usuário",
            bootstyle=DANGER,
            command=self.excluir_usuario
        ).grid(row=0, column=2, padx=10)

        tb.Button(
            btn_frame,
            text="🔄 Atualizar Lista",
            bootstyle=SECONDARY,
            command=self.carregar_usuarios
        ).grid(row=0, column=3, padx=10)

        tb.Button(
            btn_frame,
            text="⬅ Voltar ao Menu",
            bootstyle=WARNING,
            command=self.voltar_menu
        ).grid(row=0, column=4, padx=10)

        # === Tabela de usuários ===
        self.tree = tb.Treeview(
            self,
            columns=("id", "username", "role"),
            show="headings",
            height=15,
            bootstyle="info"
        )
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Usuário")
        self.tree.heading("role", text="Papel")

        self.tree.column("id", width=60, anchor=CENTER)
        self.tree.column("username", width=200, anchor=W)
        self.tree.column("role", width=100, anchor=CENTER)

        self.carregar_usuarios()

        logger.info(f"Administrador '{self.user_logado}' abriu o módulo de gerenciamento de usuários.")

    # === Funções de CRUD ===

    def carregar_usuarios(self):
        """Carrega todos os usuários cadastrados."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            usuarios = User.listar_usuarios()
            for u in usuarios:
                self.tree.insert("", END, values=u)
            logger.info(f"{len(usuarios)} usuários listados no painel de administração.")
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao carregar lista de usuários.")

    def adicionar_usuario(self):
        """Cria um novo usuário."""
        username = askstring("Novo Usuário", "Digite o nome de usuário:")
        if not username:
            return

        password = askstring("Senha", f"Digite a senha para '{username}':")
        if not password:
            return

        role = askstring("Papel", "Digite o papel do usuário (user/admin):", initialvalue="user")
        if not role:
            return

        try:
            User.registrar(username, password, role)
            Log.registrar(self.user_logado, f"criou_usuario({username})")
            messagebox.showinfo("Sucesso", f"Usuário '{username}' criado com sucesso.")
            logger.info(f"Usuário '{username}' criado por '{self.user_logado}'.")
            self.carregar_usuarios()
        except Exception as e:
            logger.error(f"Erro ao criar usuário '{username}': {e}", exc_info=True)
            messagebox.showerror("Erro", str(e))

    def alterar_role(self):
        """Altera o papel (role) de um usuário selecionado."""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return

        username = self.tree.item(item)["values"][1]
        novo_role = askstring("Alterar Papel", f"Novo papel para '{username}':", initialvalue="user")

        if not novo_role:
            return

        try:
            User.alterar_role(username, novo_role)
            Log.registrar(self.user_logado, f"alterou_role({username}→{novo_role})")
            messagebox.showinfo("Sucesso", f"Papel de '{username}' alterado para '{novo_role}'.")
            logger.info(f"Administrador '{self.user_logado}' alterou o papel de '{username}' para '{novo_role}'.")
            self.carregar_usuarios()
        except Exception as e:
            logger.error(f"Erro ao alterar papel de '{username}': {e}", exc_info=True)
            messagebox.showerror("Erro", str(e))

    def excluir_usuario(self):
        """Exclui o usuário selecionado."""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return

        username = self.tree.item(item)["values"][1]

        if username == "admin_master":
            messagebox.showwarning("Aviso", "O administrador principal não pode ser excluído.")
            return

        confirmar = messagebox.askyesno("Confirmação", f"Deseja excluir o usuário '{username}'?")
        if not confirmar:
            return

        try:
            User.excluir_usuario(username, self.user_logado)
            Log.registrar(self.user_logado, f"excluiu_usuario({username})")
            messagebox.showinfo("Sucesso", f"Usuário '{username}' excluído com sucesso.")
            logger.info(f"Usuário '{username}' excluído por '{self.user_logado}'.")
            self.carregar_usuarios()
        except Exception as e:
            logger.error(f"Erro ao excluir usuário '{username}': {e}", exc_info=True)
            messagebox.showerror("Erro", str(e))

    def voltar_menu(self):
        """Volta ao menu principal."""
        for widget in self.master.winfo_children():
            widget.destroy()
        from APP.ui.main_app import MainApp
        MainApp(self.master, self.user_logado, self.role)
