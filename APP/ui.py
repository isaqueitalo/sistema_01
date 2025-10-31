# APP/ui.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, Toplevel, ttk
from tkinter.simpledialog import askstring
from APP.config import APP_TITLE, WINDOW_SIZE
from APP.controllers import UserController


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.style = tb.Style(theme="cyborg")

        frame = tb.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tb.Label(frame, text="🔐 Sistema de Login", font=("Segoe UI", 18, "bold"),
                 bootstyle="info").pack(pady=(0, 20))

        tb.Label(frame, text="Usuário:", font=("Segoe UI", 11)).pack(anchor="w")
        self.username_entry = tb.Entry(frame, width=30)
        self.username_entry.pack(pady=5)

        tb.Label(frame, text="Senha:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        self.password_entry = tb.Entry(frame, show="*", width=30)
        self.password_entry.pack(pady=5)

        self.mostrar_senha = tb.BooleanVar(value=False)
        tb.Checkbutton(frame, text="Mostrar senha", variable=self.mostrar_senha,
                       bootstyle="round-toggle", command=self.toggle_password).pack(anchor="w", pady=(5, 0))

        btn_frame = tb.Frame(frame)
        btn_frame.pack(pady=20)

        tb.Button(btn_frame, text="Entrar", width=12, bootstyle=SUCCESS,
                  command=self.login_action).grid(row=0, column=0, padx=5)
        tb.Button(btn_frame, text="Criar Usuário", width=12, bootstyle=INFO,
                  command=self.register_action).grid(row=0, column=1, padx=5)
        tb.Button(btn_frame, text="Sair", width=12, bootstyle=DANGER,
                  command=self.root.destroy).grid(row=0, column=2, padx=5)

    # === Funções ===
    def toggle_password(self):
        self.password_entry.config(show="" if self.mostrar_senha.get() else "*")

    def login_action(self):
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        ok, role = UserController.autenticar_usuario(user, password)
        if ok and role == "admin":
            self.abrir_painel_admin(user)

    def register_action(self):
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = askstring("Confirmação", "Digite novamente a senha:")
        UserController.criar_usuario(user, password, confirm)

    # === Painel Administrativo ===
    def abrir_painel_admin(self, admin_user):
        admin_win = tb.Toplevel(self.root)
        admin_win.title(f"Painel Administrativo - {admin_user}")
        admin_win.geometry("700x500")

        tb.Label(admin_win, text="👑 Gerenciamento de Usuários",
                 font=("Segoe UI", 14, "bold"), bootstyle="primary").pack(pady=10)

        cols = ("ID", "Usuário", "Papel")
        self.tree = tb.Treeview(admin_win, columns=cols, show="headings", bootstyle="info")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tb.Frame(admin_win)
        btn_frame.pack(pady=15)
        tb.Button(btn_frame, text="🔄 Atualizar", width=18, bootstyle=INFO,
                  command=self.atualizar_lista).grid(row=0, column=0, padx=8, pady=5)
        tb.Button(btn_frame, text="➕ Novo Usuário", width=18, bootstyle=SUCCESS,
                  command=self.criar_usuario_admin).grid(row=0, column=1, padx=8, pady=5)
        tb.Button(btn_frame, text="❌ Excluir Selecionado", width=18, bootstyle=DANGER,
                  command=lambda: self.excluir_usuario(admin_user)).grid(row=0, column=2, padx=8, pady=5)
        tb.Button(btn_frame, text="📜 Ver Logs", width=18, bootstyle=SECONDARY,
                  command=self.ver_logs).grid(row=0, column=3, padx=8, pady=5)

        tb.Button(btn_frame, text="⬆ Tornar Admin", width=18, bootstyle=WARNING,
                  command=lambda: self.alterar_role_usuario("admin")).grid(row=1, column=0, padx=8, pady=5)
        tb.Button(btn_frame, text="⬇ Tornar Usuário", width=18, bootstyle=SECONDARY,
                  command=lambda: self.alterar_role_usuario("user")).grid(row=1, column=1, padx=8, pady=5)

        self.atualizar_lista()

    def atualizar_lista(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        users = UserController.obter_lista_usuarios()
        for u in users:
            self.tree.insert("", "end", values=u)

    def criar_usuario_admin(self):
        username = askstring("Novo Usuário", "Digite o nome do usuário:")
        password = askstring("Senha", "Digite a senha:")
        confirm = askstring("Confirme a senha", "Digite novamente:")
        UserController.criar_usuario(username, password, confirm)
        self.atualizar_lista()

    def excluir_usuario(self, executor):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        user = self.tree.item(selected[0], "values")[1]
        UserController.excluir_usuario(user, executor)
        self.atualizar_lista()

    def alterar_role_usuario(self, novo_role):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        user = self.tree.item(selected[0], "values")[1]
        UserController.alterar_role(user, novo_role)
        self.atualizar_lista()

    def ver_logs(self):
        logs = UserController.obter_logs()
        log_win = tb.Toplevel(self.root)
        log_win.title("📜 Logs de Atividades")
        log_win.geometry("600x400")

        cols = ("Usuário", "Ação", "Data/Hora")
        tree = tb.Treeview(log_win, columns=cols, show="headings", bootstyle="info")
        for col in cols:
            tree.heading(col, text=col)
        for log in logs:
            tree.insert("", "end", values=log)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
