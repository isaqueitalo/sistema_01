import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter.simpledialog import askstring

# 🔑 Importações atualizadas, assumindo que modelos e config estão no mesmo nível de APP
from APP.models import User, Log
from APP.config import APP_TITLE, WINDOW_SIZE

# 🚨 IMPORTAÇÃO DO NOVO MENU PRINCIPAL
# Vamos assumir que a classe do Menu Principal será MainApp
# Ela precisa ser importada para ser chamada após o login
from APP.ui.main_app import MainApp 


# 🚨 CLASSE RENOMEADA: Foco apenas na interface de Login
class LoginUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        # Tema moderno (mantido)
        self.style = tb.Style(theme="cyborg")

        # ... (Restante do __init__ - Mantido igual) ...
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
        """Realiza o login. Se for sucesso, abre o Menu Principal."""
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            ok, role = User.autenticar(user, password)
            if ok:
                messagebox.showinfo("Sucesso", f"Bem-vindo, {user}!")
                
                # 🚨 MUDANÇA: Destruímos a tela de login e chamamos o Menu Principal
                self.root.withdraw()  # Esconde a janela de login
                MainApp(self.root, user, role) # Cria a nova UI no topo do 'root'
                
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
            
    # 🚨 REMOVEMOS todas as funções de Painel Admin (ver_logs, atualizar_lista, etc.) daqui.
    # Elas serão criadas DENTRO do novo módulo do Menu Principal (MainApp)