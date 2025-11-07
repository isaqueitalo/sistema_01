import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox


class LogsViewer(tb.Frame):
    """Tela para o administrador visualizar e filtrar logs do sistema."""

    def __init__(self, master, usuario_logado: str):
        super().__init__(master)
        self.master = master
        self.usuario = usuario_logado
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 🔒 Restrição: apenas admin_master pode acessar
        if self.usuario != "admin_master":
            messagebox.showwarning("Acesso negado", "Apenas o administrador pode visualizar os logs.")
            self.master.destroy()
            return

        tb.Label(
            self,
            text="📜 Logs do Sistema",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 10))

        # === Área de filtros ===
        filtro_frame = tb.Frame(self)
        filtro_frame.pack(fill=X, pady=(0, 10))

        tb.Label(
            filtro_frame,
            text="🔍 Buscar:",
            font=("Segoe UI", 10, "bold")
        ).pack(side=LEFT, padx=(0, 5))

        self.search_var = tb.StringVar()
        search_entry = tb.Entry(filtro_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.exibir_logs())

        tb.Button(
            filtro_frame,
            text="Filtrar",
            bootstyle=INFO,
            command=self.exibir_logs
        ).pack(side=LEFT, padx=5)

        tb.Button(
            filtro_frame,
            text="Limpar Filtro",
            bootstyle=SECONDARY,
            command=self.limpar_filtro
        ).pack(side=LEFT, padx=5)

        tb.Button(
            filtro_frame,
            text="🔄 Atualizar",
            bootstyle=SUCCESS,
            command=self.exibir_logs
        ).pack(side=LEFT, padx=10)

        tb.Button(
            filtro_frame,
            text="⬅ Voltar",
            bootstyle=DANGER,
            command=self.voltar_menu
        ).pack(side=RIGHT, padx=5)

        # === Área do log ===
        self.text_area = ScrolledText(self, wrap="word", height=35, width=115)
        self.text_area.pack(fill=BOTH, expand=True)
        self.text_area.configure(state="disabled", font=("Consolas", 10))

        self.exibir_logs()

    # === Exibição dos logs ===
    def exibir_logs(self):
        """Carrega, filtra e exibe as últimas linhas do arquivo de log."""
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")

        log_path = os.path.join(os.path.dirname(__file__), "..", "..", "DATA", "system.log")
        log_path = os.path.abspath(log_path)

        termo_busca = self.search_var.get().strip().lower()
        linhas_filtradas = []

        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                linhas = f.readlines()[-1000:]  # últimas 1000 linhas
                if termo_busca:
                    linhas_filtradas = [l for l in linhas if termo_busca in l.lower()]
                else:
                    linhas_filtradas = linhas

            if not linhas_filtradas:
                self.text_area.insert("end", f"⚠️ Nenhum resultado encontrado para: '{termo_busca}'.\n")
            else:
                for linha in linhas_filtradas:
                    tag = self._detectar_tag(linha)
                    self.text_area.insert("end", linha, tag)
        else:
            self.text_area.insert("end", "⚠️ Arquivo de log não encontrado.\n")

        # === Cores ===
        self.text_area.tag_config("erro", foreground="red")
        self.text_area.tag_config("aviso", foreground="orange")
        self.text_area.tag_config("info", foreground="cyan")
        self.text_area.tag_config("debug", foreground="gray")

        self.text_area.configure(state="disabled")
        self.text_area.see("end")  # rola até o final

    def limpar_filtro(self):
        """Limpa o campo de busca e exibe todos os logs novamente."""
        self.search_var.set("")
        self.exibir_logs()

    def _detectar_tag(self, linha: str) -> str:
        """Detecta a categoria do log para colorir."""
        if "CRITICAL" in linha or "ERROR" in linha:
            return "erro"
        elif "WARNING" in linha:
            return "aviso"
        elif "INFO" in linha:
            return "info"
        else:
            return "debug"

    def voltar_menu(self):
        """Volta ao menu principal."""
        for widget in self.master.winfo_children():
            widget.destroy()
        from APP.ui.main_app import MainApp
        MainApp(self.master, self.usuario, "admin")
