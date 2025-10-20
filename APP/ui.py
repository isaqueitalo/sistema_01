import tkinter as tk
from tkinter import ttk, messagebox
from APP.models import User
from APP.config import APP_TITLE, WINDOW_SIZE

# Estilo moderno com ttkbootstrap (precisa instalar com: pip install ttkbootstrap)
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        # Tema moderno
        self.style = tb.Style(theme="cyborg")  # opções: flatly, darkly, cosmo, cyborg, etc.

        # Frame principal centralizado
        frame = tb.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        tb.Label(frame, text="🔐 Sistema de Login", font=("Segoe UI", 18, "bold"), bootstyle="info").pack(pady=(0, 20))

        # Campo Usuário
        tb.Label(frame, text="Usuário:", font=("Segoe UI", 11)).pack(anchor="w")
        self.username_entry = tb.Entry(frame, width=30)
        self.username_entry.pack(pady=5)

        # Campo Senha
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
            u = User(user, password)
            if u.login():
                messagebox.showinfo("Sucesso", f"Bem-vindo, {user}!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def register_action(self):
        user = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            u = User(user, password)
            u.register()
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
