import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from APP.config import APP_TITLE


class MainApp:
    def __init__(self, root, username, role):
        self.root = root       # janela principal (Tk)
        self.username = username
        self.role = role

        # === Criar uma nova janela (Toplevel) ===
        self.win = tb.Toplevel(self.root)
        self.win.title(f"{APP_TITLE} - Menu Principal ({self.role})")
        self.win.geometry("800x600")
        self.win.resizable(True, True)

        # === Frame principal ===
        self.main_frame = tb.Frame(self.win, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        tb.Label(
            self.main_frame,
            text=f"Olá, {self.username}! Seu perfil é: {self.role.upper()}",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=20)

        # === Menu de botões ===
        self.button_frame = tb.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.criar_menu_botoes()

    def criar_menu_botoes(self):
        """Cria os botões do menu com base no papel do usuário (role)."""

        menu_items = [
            ("💰 Registrar Venda (PDV)", self.abrir_vendas, SUCCESS, ["admin", "vendedor"]),
            ("📦 Gerenciar Produtos", self.abrir_produtos, INFO, ["admin", "estoquista"]),
            ("👥 Gerenciar Clientes", self.abrir_clientes, INFO, ["admin", "vendedor", "estoquista"]),
            ("📊 Relatórios e Dashboards", self.abrir_relatorios, WARNING, ["admin"]),
            ("🧑‍💻 Gerenciar Usuários", self.abrir_usuarios, DANGER, ["admin"]),
            ("📝 Ver Logs de Atividade", self.ver_logs, SECONDARY, ["admin"])
        ]

        row = 0
        for text, command, style, allowed_roles in menu_items:
            if self.role in allowed_roles:
                tb.Button(
                    self.button_frame,
                    text=text,
                    width=30,
                    bootstyle=style,
                    command=command
                ).grid(row=row, column=0, padx=10, pady=10)
                row += 1

        # Botão de Logout (sempre visível)
        tb.Button(
            self.button_frame,
            text="🚪 Sair / Logout",
            width=30,
            bootstyle=SECONDARY,
            command=self.logout
        ).grid(row=row + 1, column=0, padx=10, pady=20)

    # === MÉTODOS DE ABERTURA DE MÓDULOS ===
    def abrir_vendas(self):
        messagebox.showinfo("Módulo Vendas", "Em desenvolvimento: Tela de Ponto de Venda (PDV)")

    def abrir_produtos(self):
        messagebox.showinfo("Módulo Produtos", "Em desenvolvimento: CRUD de produtos.")

    def abrir_clientes(self):
        messagebox.showinfo("Módulo Clientes", "Em desenvolvimento: cadastro de clientes.")

    def abrir_relatorios(self):
        messagebox.showinfo("Módulo Relatórios", "Em desenvolvimento: dashboards e gráficos.")

    def abrir_usuarios(self):
        messagebox.showinfo("Módulo Usuários", "Em desenvolvimento: painel administrativo.")

    def ver_logs(self):
        messagebox.showinfo("Logs", "Visualização dos logs em breve!")

    def logout(self):
        """Fecha o menu principal e retorna à tela de login."""
        self.win.destroy()
        self.root.deiconify()  # Mostra novamente a tela de login
