# APP/ui.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter.simpledialog import askstring
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

        # Frame principal centralizado
        frame = tb.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        tb.Label(
            frame,
            text="🔐 Sistema de Login",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 20))

        # Campo Usuário
        tb.Label(frame, text="Usuário:", font=("Segoe UI", 11)).pack(anchor="w")
        self.username_entry = tb.Entry(frame, width=30)
        self.username_entry.pack(pady=5)

        # Campo Senha
        tb.Label(frame, text="Senha:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        self.password_entry = tb.Entry(frame, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Mostrar senha
        self.mostrar_senha = tb.BooleanVar(value=False)
        tb.Checkbutton(
            frame,
            text="Mostrar senha",
            variable=self.mostrar_senha,
            bootstyle="round-toggle",
            command=self.toggle_password
        ).pack(anchor="w", pady=(5, 0))

        # Botões principais
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
        """Alterna entre mostrar e esconder a senha."""
        if self.mostrar_senha.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def login_action(self):
        """Realiza o login."""
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
        """Cria novo usuário com confirmação de senha."""
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not user or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        password2 = askstring("Confirmação", "Digite novamente a senha:")

        if not password2:
            messagebox.showwarning("Aviso", "Confirmação de senha cancelada.")
            return
        if password != password2:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return

        try:
            User.registrar(user, password)
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # === Painel Administrativo ===
    def abrir_painel_admin(self, admin_user):
        """Abre a janela de gerenciamento de usuários."""
        admin_win = tb.Toplevel(self.root)
        admin_win.title(f"Painel Administrativo - {admin_user}")
        admin_win.geometry("600x450")

        tb.Label(
            admin_win,
            text="👑 Gerenciamento de Usuários",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary"
        ).pack(pady=10)

        # Tabela de usuários
        cols = ("ID", "Usuário", "Papel")
        self.tree = tb.Treeview(admin_win, columns=cols, show="headings", bootstyle="info")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Botões administrativos
        btn_frame = tb.Frame(admin_win)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="🔄 Atualizar", width=12, bootstyle=INFO,
                  command=self.atualizar_lista).grid(row=0, column=0, padx=5)
        tb.Button(btn_frame, text="➕ Novo Usuário", width=15, bootstyle=SUCCESS,
                  command=self.criar_usuario_admin).grid(row=0, column=1, padx=5)
        tb.Button(btn_frame, text="❌ Excluir Selecionado", width=18, bootstyle=DANGER,
                  command=lambda: self.excluir_usuario(admin_user)).grid(row=0, column=2, padx=5)

        # Novos botões: alterar papel
        tb.Button(btn_frame, text="⬆ Tornar Admin", width=15, bootstyle=WARNING,
                  command=lambda: self.alterar_role_usuario("admin")).grid(row=1, column=0, padx=5, pady=5)
        tb.Button(btn_frame, text="⬇ Tornar Usuário", width=15, bootstyle=SECONDARY,
                  command=lambda: self.alterar_role_usuario("user")).grid(row=1, column=1, padx=5, pady=5)

        self.atualizar_lista()

    def atualizar_lista(self):
        """Recarrega a tabela de usuários."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        users = User.listar_usuarios()
        for u in users:
            self.tree.insert("", "end", values=u)

    def criar_usuario_admin(self):
        """Cria novo usuário a partir do painel admin."""
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
        """Exclui usuário selecionado (exceto o admin)."""
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

    def alterar_role_usuario(self, novo_role):
        """Muda o papel de um usuário."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        user = self.tree.item(selected[0], "values")[1]
        try:
            User.alterar_role(user, novo_role)
            messagebox.showinfo("Sucesso", f"Papel de '{user}' alterado para {novo_role}.")
            self.atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
