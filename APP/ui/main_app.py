import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from APP.logger import logger


class MainApp(tb.Frame):
    """Tela principal do sistema após o login."""

    def __init__(self, master, user: str, role: str):
        super().__init__(master)
        self.master = master
        self.user = user
        self.role = role

        self.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # === Cabeçalho ===
        header = tb.Frame(self)
        header.pack(fill=X, pady=(0, 20))

        tb.Label(
            header,
            text=f"👋 Bem-vindo, {self.user} ({self.role})",
            font=("Segoe UI", 16, "bold"),
            bootstyle="info"
        ).pack(side=LEFT)

        tb.Button(
            header,
            text="🚪 Sair",
            bootstyle=DANGER,
            command=self.voltar_login
        ).pack(side=RIGHT, padx=10)

        tb.Separator(self, bootstyle="secondary").pack(fill=X, pady=5)

        # === Corpo principal ===
        frame_botoes = tb.Frame(self)
        frame_botoes.pack(pady=30)

        tb.Label(
            frame_botoes,
            text="Menu Principal",
            font=("Segoe UI", 14, "bold"),
            bootstyle="secondary"
        ).pack(pady=(0, 20))

        # === Botões comuns ===
        tb.Button(
            frame_botoes,
            text="🛒 Gerenciar Produtos",
            width=25,
            bootstyle=PRIMARY,
            command=self.abrir_produtos
        ).pack(pady=5)

        # === Painel do vendedor (role=user) ===
        if self.role == "user":
            tb.Button(
                frame_botoes,
                text="🧾 Painel de Vendas",
                width=25,
                bootstyle=SUCCESS,
                command=self.abrir_painel_vendedor
            ).pack(pady=5)

        # === Ferramentas administrativas ===
        if self.role in ("admin", "admin_master"):
            tb.Separator(frame_botoes, bootstyle="secondary").pack(fill=X, pady=10)

            tb.Label(
                frame_botoes,
                text="Ferramentas do Administrador",
                font=("Segoe UI", 12, "bold"),
                bootstyle="warning"
            ).pack(pady=(10, 5))

            tb.Button(
                frame_botoes,
                text="👥 Gerenciar Usuários",
                width=25,
                bootstyle=INFO,
                command=self.abrir_usuarios
            ).pack(pady=5)

            tb.Button(
                frame_botoes,
                text="⚙️ Configurações do Sistema",
                width=25,
                bootstyle=SECONDARY,
                command=self.configuracoes
            ).pack(pady=5)

        # === Somente admin_master vê logs ===
        if self.user == "admin_master":
            tb.Button(
                frame_botoes,
                text="📜 Ver Logs do Sistema",
                width=25,
                bootstyle=WARNING,
                command=self.abrir_logs
            ).pack(pady=5)

        logger.info(f"Usuário '{self.user}' entrou no sistema (role={self.role}).")

    # === Funções de navegação ===

    def abrir_produtos(self):
        """Abre o módulo de produtos."""
        try:
            for widget in self.master.winfo_children():
                widget.destroy()
            from APP.ui.produtos_ui import ProdutosUI
            ProdutosUI(self.master, self.user, self.role)
            logger.info(f"Usuário '{self.user}' abriu o módulo de produtos.")
        except Exception as e:
            logger.error(f"Erro ao abrir módulo de produtos: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao abrir a tela de produtos. Verifique os logs.")

    def abrir_painel_vendedor(self):
        """Abre o painel de vendas (usuário comum)."""
        try:
            for widget in self.master.winfo_children():
                widget.destroy()
            from APP.ui.vendedor_ui import VendedorUI
            VendedorUI(self.master, self.user)
            logger.info(f"Usuário '{self.user}' acessou o painel de vendedor.")
        except Exception as e:
            logger.error(f"Erro ao abrir painel de vendedor: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao abrir o painel de vendas.")

    def abrir_usuarios(self):
        """Abre o módulo de gerenciamento de usuários (somente admin)."""
        try:
            for widget in self.master.winfo_children():
                widget.destroy()
            from APP.ui.usuarios_ui import UsuariosUI
            UsuariosUI(self.master, self.user, self.role)
            logger.info(f"Administrador '{self.user}' abriu o módulo de usuários.")
        except Exception as e:
            logger.error(f"Erro ao abrir módulo de usuários: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao abrir a tela de usuários.")

    def abrir_logs(self):
        """Abre o visualizador de logs (somente admin_master)."""
        if self.user != "admin_master":
            messagebox.showwarning("Acesso negado", "Apenas o administrador principal pode visualizar os logs.")
            logger.warning(f"Tentativa de acesso não autorizado aos logs por '{self.user}'.")
            return

        try:
            for widget in self.master.winfo_children():
                widget.destroy()
            from APP.ui.logs_viewer import LogsViewer
            LogsViewer(self.master, self.user)
            logger.info(f"Administrador '{self.user}' abriu o visualizador de logs.")
        except Exception as e:
            logger.error(f"Erro ao abrir visualizador de logs: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao abrir o visualizador de logs.")

    def configuracoes(self):
        """Tela de configurações (placeholder)."""
        messagebox.showinfo("Configurações", "Módulo de configurações ainda em desenvolvimento.")
        logger.info(f"Usuário '{self.user}' acessou o módulo de configurações.")

    def voltar_login(self):
        """Retorna à tela de login."""
        try:
            for widget in self.master.winfo_children():
                widget.destroy()
            from APP.ui.login_ui import LoginUI
            LoginUI(self.master)
            logger.info(f"Usuário '{self.user}' saiu do sistema e retornou à tela de login.")
        except Exception as e:
            logger.error(f"Erro ao voltar à tela de login: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao retornar à tela de login.")
