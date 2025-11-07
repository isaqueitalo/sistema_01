import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter.simpledialog import askinteger
from APP.models.usuarios_models import Log
from APP.logger import logger
from APP.database import conectar


class VendedorUI(tb.Frame):
    """Tela principal de uso do vendedor com controle de vendas reais."""

    def __init__(self, master, user: str):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # === Cabeçalho ===
        header = tb.Frame(self)
        header.pack(fill=X, pady=(0, 20))

        tb.Label(
            header,
            text=f"🧾 Painel de Vendas — {self.user}",
            font=("Segoe UI", 16, "bold"),
            bootstyle="info"
        ).pack(side=LEFT)

        tb.Button(
            header,
            text="🚪 Sair",
            bootstyle=DANGER,
            command=self.voltar_menu
        ).pack(side=RIGHT, padx=10)

        tb.Separator(self, bootstyle="secondary").pack(fill=X, pady=5)

        # === Botões principais ===
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(
            btn_frame,
            text="🛒 Registrar Venda",
            width=20,
            bootstyle=SUCCESS,
            command=self.registrar_venda
        ).grid(row=0, column=0, padx=10)

        tb.Button(
            btn_frame,
            text="📦 Atualizar Produtos",
            width=20,
            bootstyle=SECONDARY,
            command=self.carregar_produtos
        ).grid(row=0, column=1, padx=10)

        tb.Button(
            btn_frame,
            text="🕒 Histórico de Vendas",
            width=20,
            bootstyle=INFO,
            command=self.ver_historico
        ).grid(row=0, column=2, padx=10)

        tb.Button(
            btn_frame,
            text="⬅ Voltar ao Menu",
            width=20,
            bootstyle=WARNING,
            command=self.voltar_menu
        ).grid(row=0, column=3, padx=10)

        # === Tabela de produtos disponíveis ===
        tb.Label(
            self,
            text="📦 Produtos Disponíveis",
            font=("Segoe UI", 13, "bold"),
            bootstyle="secondary"
        ).pack(pady=(10, 5))

        self.tree = tb.Treeview(
            self,
            columns=("id", "nome", "preco", "estoque"),
            show="headings",
            height=12,
            bootstyle="info"
        )
        self.tree.pack(fill=BOTH, expand=True, pady=5)

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome do Produto")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("estoque", text="Estoque")

        self.tree.column("id", width=60, anchor=CENTER)
        self.tree.column("nome", width=250, anchor=W)
        self.tree.column("preco", width=100, anchor=E)
        self.tree.column("estoque", width=100, anchor=CENTER)

        self.carregar_produtos()
        logger.info(f"Vendedor '{self.user}' abriu o painel de vendas.")

    # === Funções de banco ===

    def carregar_produtos(self):
        """Carrega produtos disponíveis no estoque."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome ASC")
            produtos = cursor.fetchall()
            conn.close()

            for p in produtos:
                self.tree.insert("", END, values=p)

            logger.info(f"{len(produtos)} produtos carregados para o vendedor '{self.user}'.")
        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao carregar lista de produtos.")

    def registrar_venda(self):
        """Permite ao vendedor registrar uma venda real."""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um produto para vender.")
            return

        produto = self.tree.item(item)["values"]
        id_produto, nome, preco, estoque = produto

        if estoque <= 0:
            messagebox.showwarning("Aviso", "Este produto está sem estoque.")
            return

        quantidade = askinteger("Quantidade", f"Quantidade vendida de '{nome}':", minvalue=1, maxvalue=estoque)
        if not quantidade:
            return

        total = round(preco * quantidade, 2)

        confirmar = messagebox.askyesno(
            "Confirmação de Venda",
            f"Produto: {nome}\nQuantidade: {quantidade}\nTotal: R$ {total:.2f}\n\nConfirmar venda?"
        )
        if not confirmar:
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            # Atualiza estoque
            cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, id_produto))

            # Registra venda
            cursor.execute(
                "INSERT INTO vendas (produto_id, vendedor, quantidade, total) VALUES (?, ?, ?, ?)",
                (id_produto, self.user, quantidade, total)
            )
            conn.commit()
            conn.close()

            Log.registrar(self.user, f"registrou_venda({nome}, qtd={quantidade}, total={total})")
            logger.info(f"Venda registrada: {nome}, {quantidade}x, total R$ {total:.2f}, vendedor={self.user}")
            messagebox.showinfo("Sucesso", f"Venda registrada!\nTotal: R$ {total:.2f}")

            self.carregar_produtos()

        except Exception as e:
            logger.error(f"Erro ao registrar venda: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao registrar venda.")

    def ver_historico(self):
        """Exibe histórico de vendas do vendedor atual."""
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.id, p.nome, v.quantidade, v.total, v.data_hora
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                WHERE v.vendedor = ?
                ORDER BY v.id DESC
            """, (self.user,))
            vendas = cursor.fetchall()
            conn.close()

            if not vendas:
                messagebox.showinfo("Histórico", "Nenhuma venda encontrada.")
                return

            # Abre nova janela de histórico
            janela = tb.Toplevel(self.master)
            janela.title("Histórico de Vendas")
            janela.geometry("700x400")

            tb.Label(
                janela,
                text=f"Histórico de Vendas — {self.user}",
                font=("Segoe UI", 14, "bold"),
                bootstyle="info"
            ).pack(pady=10)

            tree_hist = tb.Treeview(
                janela,
                columns=("id", "produto", "quantidade", "total", "data"),
                show="headings",
                height=15,
                bootstyle="info"
            )
            tree_hist.pack(fill=BOTH, expand=True, padx=10, pady=10)

            tree_hist.heading("id", text="ID")
            tree_hist.heading("produto", text="Produto")
            tree_hist.heading("quantidade", text="Qtd")
            tree_hist.heading("total", text="Total (R$)")
            tree_hist.heading("data", text="Data / Hora")

            for v in vendas:
                tree_hist.insert("", END, values=v)

            Log.registrar(self.user, "visualizou_historico_vendas")
            logger.info(f"Usuário '{self.user}' abriu o histórico de vendas.")
        except Exception as e:
            logger.error(f"Erro ao exibir histórico de vendas: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao carregar histórico de vendas.")

    def voltar_menu(self):
        """Volta ao menu principal."""
        for widget in self.master.winfo_children():
            widget.destroy()
        from APP.ui.main_app import MainApp
        MainApp(self.master, self.user, "user")
        logger.info(f"Usuário '{self.user}' retornou ao menu principal.")
