# APP/ui.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from APP.models import User
from APP.config import APP_TITLE, WINDOW_SIZE


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        # Tema moderno
        self.style = tb.Style(theme="cyborg")

        # Frame principal
        frame = tb.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tb.Label(
            frame,
            text="🔐 Sistema de Login",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 20))

        tb.Label(frame, text="Usuário:", font=("Segoe UI", 11)).pack(anchor="w")
        self.username_entry = tb.Entry(frame, width=30)
        self.username_entry.pack(pady=5)

        tb.Label(frame, text="Senha:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        self.password_entry = tb.Entry(frame, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Botões
        btn_frame = tb.Frame(frame)
        btn_frame.pack(pady=20)

        tb.Button(btn_frame, text="Entrar", width=12, bootstyle=SUCCESS, command=self.login_action).grid(row=0, column=0, padx=5)
        tb.Button(btn_frame, text="Criar Usuário", width=12, bootstyle=INFO, command=self.register_action).grid(row=0, column=1, padx=5)
        tb.Button(btn_frame, text="Sair", width=12, bootstyle=DANGER, command=self.root.destroy).grid(row=0, column=2, padx=5)

    # === Funções ===
    def login_action(self):
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            ok, role = User.autenticar(user, password)
            if ok:
                messagebox.showinfo("Sucesso", f"Bem-vindo, {user}!")
                if role == "admin":
                    self.abrir_painel_admin(user)
            else:
                messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def register_action(self):
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            User.registrar(user, password)
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # === Tela de administração ===
    def abrir_painel_admin(self, admin_user):
        admin_win = tb.Toplevel(self.root)
        admin_win.title(f"Painel Administrativo - {admin_user}")
        admin_win.geometry("500x400")

        tb.Label(
            admin_win,
            text="👑 Gerenciamento de Usuários",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary"
        ).pack(pady=10)

        # Tabela
        cols = ("ID", "Usuário", "Papel")
        self.tree = tb.Treeview(admin_win, columns=cols, show="headings", bootstyle="info")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Botões
        btn_frame = tb.Frame(admin_win)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="🔄 Atualizar", width=12, bootstyle=INFO, command=self.atualizar_lista).grid(row=0, column=0, padx=5)
        tb.Button(btn_frame, text="➕ Novo Usuário", width=15, bootstyle=SUCCESS, command=self.criar_usuario_admin).grid(row=0, column=1, padx=5)
        tb.Button(btn_frame, text="❌ Excluir Selecionado", width=18, bootstyle=DANGER, command=lambda: self.excluir_usuario(admin_user)).grid(row=0, column=2, padx=5)

        self.atualizar_lista()

    def atualizar_lista(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        users = User.listar_usuarios()
        for u in users:
            self.tree.insert("", "end", values=u)

    def criar_usuario_admin(self):
        from tkinter.simpledialog import askstring
        username = askstring("Novo Usuário", "Digite o nome do usuário:")
        password = askstring("Senha", "Digite a senha do usuário:")
        if username and password:
            try:
                User.registrar(username, password)
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                self.atualizar_lista()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def excluir_usuario(self, executor):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir.")
            return
        user = self.tree.item(selected[0], "values")[1]
        try:
            User.excluir_usuario(user, executor)
            messagebox.showinfo("Sucesso", f"Usuário '{user}' excluído.")
            self.atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
