import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, ttk

# Importações de config e modelos
from APP.config import APP_TITLE
from APP.models.usuarios_models import Log


class MainApp:
    def __init__(self, master, username, role):
        self.master = master
        self.username = username
        self.role = role
        
        # Configuração da janela principal
        master.title(f"{APP_TITLE} - Menu Principal ({self.role})")
        master.geometry("800x600")
        master.resizable(True, True)

        # Frame principal
        self.main_frame = tb.Frame(master, padding=20)
        self.main_frame.pack(fill="both", expand=True)
        
        # Título
        tb.Label(
            self.main_frame,
            text=f"Olá, {self.username}! Seu perfil é: {self.role.upper()}",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=20)
        
        # Frame dos botões
        self.button_frame = tb.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        self.criar_menu_botoes()

    def criar_menu_botoes(self):
        """Cria os botões do menu com base no papel do usuário."""
        menu_items = [
            ("Registrar Venda (PDV)", self.abrir_vendas, SUCCESS, ["admin", "vendedor"]),
            ("Gerenciar Produtos", self.abrir_produtos, INFO, ["admin", "estoquista"]),
            ("Gerenciar Clientes", self.abrir_clientes, INFO, ["admin", "estoquista", "vendedor"]),
            ("Relatórios/Dashboards", self.abrir_relatorios, WARNING, ["admin"]),
            ("Gerenciar Usuários", self.abrir_usuarios, DANGER, ["admin"]),
            ("Ver Logs / Auditoria", self.abrir_logs, SECONDARY, ["admin"]),
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

        tb.Button(
            self.button_frame,
            text="Sair / Logout",
            width=30,
            bootstyle=(DANGER, OUTLINE),
            command=self.logout
        ).grid(row=row + 1, column=0, padx=10, pady=20)

    # === MÉTODOS DE MÓDULOS ===
    def abrir_vendas(self):
        messagebox.showinfo("Módulo Vendas", "Em desenvolvimento: Tela de Ponto de Venda (PDV)")

    def abrir_produtos(self):
        """Abre o módulo de gerenciamento de produtos."""
        try:
            from APP.ui.produtos_ui import ProdutosUI
            ProdutosUI(self.master, self.username, self.role)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Erro", f"Falha ao abrir o módulo de produtos:\n{e}")



    def abrir_clientes(self):
        messagebox.showinfo("Módulo Clientes", "Em desenvolvimento: Tela de Clientes")

    def abrir_relatorios(self):
        messagebox.showinfo("Módulo Relatórios", "Em desenvolvimento: Tela de Relatórios")

    def abrir_usuarios(self):
        messagebox.showinfo("Módulo Usuários", "Em desenvolvimento: Gerenciamento de Usuários")

    # === NOVO MÉTODO: VISUALIZAR LOGS ===
    def abrir_logs(self):
        """Abre uma janela com todos os registros de atividades."""
        logs = Log.listar()

        janela = tb.Toplevel(self.master)
        janela.title("📜 Logs de Atividades do Sistema")
        janela.geometry("700x400")
        janela.resizable(True, True)

        tb.Label(
            janela,
            text="Registros de Atividades",
            font=("Segoe UI", 14, "bold"),
            bootstyle="info"
        ).pack(pady=10)

        frame = tb.Frame(janela, padding=10)
        frame.pack(fill="both", expand=True)

        colunas = ("usuario", "acao", "data_hora")
        tree = ttk.Treeview(frame, columns=colunas, show="headings")
        tree.heading("usuario", text="Usuário")
        tree.heading("acao", text="Ação")
        tree.heading("data_hora", text="Data e Hora")

        # Largura das colunas
        tree.column("usuario", width=150)
        tree.column("acao", width=300)
        tree.column("data_hora", width=180)

        # Inserir os logs
        for usuario, acao, data_hora in logs:
            tree.insert("", "end", values=(usuario, acao, data_hora))

        # Barra de rolagem
        scroll = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # Botão para atualizar
        tb.Button(
            janela,
            text="🔄 Atualizar",
            bootstyle=INFO,
            command=lambda: self.atualizar_logs(tree)
        ).pack(pady=10)

    def atualizar_logs(self, tree):
        """Atualiza os registros exibidos."""
        for item in tree.get_children():
            tree.delete(item)
        for usuario, acao, data_hora in Log.listar():
            tree.insert("", "end", values=(usuario, acao, data_hora))

    # === LOGOUT ===
    def logout(self):
        """Retorna à tela de login."""
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.geometry("400x400")
        self.master.resizable(False, False)
        from APP.ui.login_ui import LoginUI 
        LoginUI(self.master)
        self.master.deiconify()
