import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter.simpledialog import askstring
from APP.models.usuarios_models import Log
from APP.logger import logger
from APP.database import conectar


class ProdutosUI(tb.Frame):
    """Tela de gerenciamento de produtos (para admins e vendedores)."""

    def __init__(self, master, user: str, role: str):
        super().__init__(master)
        self.master = master
        self.user = user
        self.role = role
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)

        tb.Label(
            self,
            text="📦 Gerenciamento de Produtos",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 15))

        # === Barra de pesquisa ===
        search_frame = tb.Frame(self)
        search_frame.pack(fill=X, pady=5)

        tb.Label(search_frame, text="🔍 Buscar produto:", bootstyle="secondary").pack(side=LEFT, padx=5)
        self.search_var = tb.StringVar()
        tb.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=LEFT, padx=5)

        tb.Button(
            search_frame,
            text="Pesquisar",
            bootstyle=INFO,
            command=self.pesquisar_produtos
        ).pack(side=LEFT, padx=5)

        tb.Button(
            search_frame,
            text="❌ Limpar",
            bootstyle=SECONDARY,
            command=self.limpar_pesquisa
        ).pack(side=LEFT, padx=5)

        # === Botões principais ===
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(
            btn_frame,
            text="➕ Adicionar Produto",
            bootstyle=SUCCESS,
            command=self.adicionar_produto
        ).grid(row=0, column=0, padx=10)

        tb.Button(
            btn_frame,
            text="✏️ Editar Produto",
            bootstyle=INFO,
            command=self.editar_produto
        ).grid(row=0, column=1, padx=10)

        tb.Button(
            btn_frame,
            text="❌ Excluir Produto",
            bootstyle=DANGER,
            command=self.excluir_produto
        ).grid(row=0, column=2, padx=10)

        tb.Button(
            btn_frame,
            text="🔄 Atualizar Lista",
            bootstyle=SECONDARY,
            command=self.carregar_produtos
        ).grid(row=0, column=3, padx=10)

        tb.Button(
            btn_frame,
            text="⬅ Voltar ao Menu",
            bootstyle=WARNING,
            command=self.voltar_menu
        ).grid(row=0, column=4, padx=10)

        # === Tabela de produtos ===
        self.tree = tb.Treeview(
            self,
            columns=("id", "nome", "preco", "estoque"),
            show="headings",
            height=15,
            bootstyle="info"
        )
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome do Produto")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("estoque", text="Estoque")

        self.tree.column("id", width=60, anchor=CENTER)
        self.tree.column("nome", width=250, anchor=W)
        self.tree.column("preco", width=100, anchor=E)
        self.tree.column("estoque", width=100, anchor=CENTER)

        self._criar_tabela_produtos()
        self.carregar_produtos()

        logger.info(f"Usuário '{self.user}' abriu o módulo de produtos (role={self.role}).")

    # === Banco de dados ===

    def _criar_tabela_produtos(self):
        """Cria tabela de produtos caso não exista."""
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    preco REAL NOT NULL,
                    estoque INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao criar tabela de produtos: {e}", exc_info=True)

    # === CRUD ===

    def carregar_produtos(self):
        """Carrega todos os produtos do banco."""
        self._limpar_tabela()

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome ASC")
            produtos = cursor.fetchall()
            conn.close()

            for p in produtos:
                self.tree.insert("", END, values=p)

            logger.info(f"{len(produtos)} produtos carregados.")
        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao carregar lista de produtos.")

    def pesquisar_produtos(self):
        """Filtra produtos pelo nome."""
        termo = self.search_var.get().strip()
        if not termo:
            self.carregar_produtos()
            return

        self._limpar_tabela()
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, preco, estoque FROM produtos WHERE nome LIKE ?", (f"%{termo}%",))
            resultados = cursor.fetchall()
            conn.close()

            if not resultados:
                messagebox.showinfo("Aviso", f"Nenhum produto encontrado contendo '{termo}'.")
            else:
                for p in resultados:
                    self.tree.insert("", END, values=p)

            Log.registrar(self.user, f"pesquisou_produto({termo})")
            logger.info(f"Usuário '{self.user}' pesquisou por '{termo}'.")

        except Exception as e:
            logger.error(f"Erro ao pesquisar produto: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao pesquisar produtos.")

    def limpar_pesquisa(self):
        """Limpa o campo de busca e recarrega todos os produtos."""
        self.search_var.set("")
        self.carregar_produtos()

    def adicionar_produto(self):
        """Adiciona um novo produto."""
        nome = askstring("Novo Produto", "Digite o nome do produto:")
        if not nome:
            return

        preco = askstring("Preço", "Digite o preço do produto (ex: 9.99):")
        if not preco:
            return

        estoque = askstring("Estoque", "Digite a quantidade em estoque:", initialvalue="0")
        if not estoque:
            estoque = 0

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
                (nome, float(preco), int(estoque))
            )
            conn.commit()
            conn.close()

            Log.registrar(self.user, f"adicionou_produto({nome})")
            logger.info(f"Usuário '{self.user}' adicionou o produto '{nome}'.")
            self.carregar_produtos()
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao adicionar produto '{nome}': {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao adicionar produto.")

    def editar_produto(self):
        """Edita o produto selecionado."""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return

        produto = self.tree.item(item)["values"]
        id_produto, nome_antigo, preco_antigo, estoque_antigo = produto

        novo_nome = askstring("Editar Produto", "Novo nome:", initialvalue=nome_antigo)
        if not novo_nome:
            return

        novo_preco = askstring("Editar Preço", "Novo preço:", initialvalue=str(preco_antigo))
        novo_estoque = askstring("Editar Estoque", "Novo estoque:", initialvalue=str(estoque_antigo))

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE produtos SET nome=?, preco=?, estoque=? WHERE id=?",
                (novo_nome, float(novo_preco), int(novo_estoque), id_produto)
            )
            conn.commit()
            conn.close()

            Log.registrar(self.user, f"editou_produto({id_produto})")
            logger.info(f"Usuário '{self.user}' editou o produto ID {id_produto}.")
            self.carregar_produtos()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao editar produto ID {id_produto}: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao editar produto.")

    def excluir_produto(self):
        """Exclui o produto selecionado."""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return

        produto = self.tree.item(item)["values"]
        id_produto, nome, _, _ = produto

        confirmar = messagebox.askyesno("Confirmação", f"Deseja excluir o produto '{nome}'?")
        if not confirmar:
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id=?", (id_produto,))
            conn.commit()
            conn.close()

            Log.registrar(self.user, f"excluiu_produto({nome})")
            logger.info(f"Usuário '{self.user}' excluiu o produto '{nome}'.")
            self.carregar_produtos()
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao excluir produto '{nome}': {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao excluir produto.")

    def _limpar_tabela(self):
        """Remove todos os registros da tabela Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)

    def voltar_menu(self):
        """Volta ao menu principal."""
        try:
            for widget in self.master.winfo_children():
                widget.destroy()
            from APP.ui.main_app import MainApp
            MainApp(self.master, self.user, self.role)
            logger.info(f"Usuário '{self.user}' retornou ao menu principal.")
        except Exception as e:
            logger.error(f"Erro ao voltar ao menu principal: {e}", exc_info=True)
            messagebox.showerror("Erro", "Falha ao retornar ao menu principal.")
