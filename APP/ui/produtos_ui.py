# APP/ui/produtos_ui.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog

from APP.controllers.produtos_controller import ProdutoController


class ProdutosUI:
    def __init__(self, master, executor, role):
        self.master = master
        self.executor = executor
        self.role = role

        # Cria janela separada
        self.window = tb.Toplevel(self.master)
        self.window.title("📦 Gerenciamento de Produtos")
        self.window.geometry("900x600")

        # Garante tabela no banco
        ProdutoController.ensure_table()

        # === TÍTULO ===
        tb.Label(
            self.window,
            text="📦 Gerenciamento de Produtos",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=15)

        # === CAMPO DE BUSCA ===
        search_frame = tb.Frame(self.window)
        search_frame.pack(pady=5)

        tb.Label(search_frame, text="Buscar Produto:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
        self.search_var = tb.StringVar()
        tb.Entry(search_frame, textvariable=self.search_var, width=40).grid(row=0, column=1, padx=5)
        tb.Button(search_frame, text="🔍 Pesquisar", bootstyle=INFO, command=self.buscar_produtos).grid(row=0, column=2, padx=5)
        tb.Button(search_frame, text="🔄 Atualizar", bootstyle=SECONDARY, command=self.atualizar_lista).grid(row=0, column=3, padx=5)

        # === TABELA ===
        cols = ("ID", "Nome", "Categoria", "Preço Venda", "Estoque", "Data Cadastro")
        self.tree = tb.Treeview(self.window, columns=cols, show="headings", bootstyle="info")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # === BOTÕES DE AÇÃO ===
        btn_frame = tb.Frame(self.window)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="➕ Novo Produto", width=18, bootstyle=SUCCESS,
                  command=self.criar_produto).grid(row=0, column=0, padx=8)

        tb.Button(btn_frame, text="✏️ Editar Produto", width=18, bootstyle=WARNING,
                  command=self.editar_produto).grid(row=0, column=1, padx=8)

        tb.Button(btn_frame, text="❌ Excluir Produto", width=18, bootstyle=DANGER,
                  command=self.excluir_produto).grid(row=0, column=2, padx=8)

        # Inicializa a listagem
        self.atualizar_lista()

    # === FUNÇÕES ===
    def atualizar_lista(self):
        """Recarrega todos os produtos."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        produtos = ProdutoController.listar_produtos()
        for p in produtos:
            self.tree.insert("", "end", values=p)

    def buscar_produtos(self):
        """Busca produtos pelo nome."""
        termo = self.search_var.get().strip()
        results = ProdutoController.buscar_por_nome(termo)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in results:
            self.tree.insert("", "end", values=p)

    def criar_produto(self):
        """Abre caixa de diálogo para novo produto."""
        nome = simpledialog.askstring("Novo Produto", "Nome do produto:")
        if not nome:
            return
        categoria = simpledialog.askstring("Categoria", "Categoria:")
        descricao = simpledialog.askstring("Descrição", "Descrição:")
        preco_custo = simpledialog.askfloat("Preço de Custo", "Digite o preço de custo:")
        preco_venda = simpledialog.askfloat("Preço de Venda", "Digite o preço de venda:")
        estoque = simpledialog.askinteger("Estoque", "Quantidade em estoque:")

        ok, msg = ProdutoController.criar_produto(
            nome, descricao, preco_custo, preco_venda, estoque, categoria,
            executor=self.executor, role=self.role
        )
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_lista()
        else:
            messagebox.showerror("Erro", msg)

    def editar_produto(self):
        """Edita o produto selecionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        item = self.tree.item(selected[0], "values")
        id_produto = item[0]
        produto = ProdutoController.obter_produto(id_produto)

        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        nome = simpledialog.askstring("Editar Produto", "Nome:", initialvalue=produto[1])
        categoria = simpledialog.askstring("Categoria", "Categoria:", initialvalue=produto[6])
        descricao = simpledialog.askstring("Descrição", "Descrição:", initialvalue=produto[2])
        preco_custo = simpledialog.askfloat("Preço de Custo", "Preço de custo:", initialvalue=produto[3])
        preco_venda = simpledialog.askfloat("Preço de Venda", "Preço de venda:", initialvalue=produto[4])
        estoque = simpledialog.askinteger("Estoque", "Estoque:", initialvalue=produto[5])

        ok, msg = ProdutoController.atualizar_produto(
            id_produto, nome, descricao, preco_custo, preco_venda, estoque, categoria,
            executor=self.executor, role=self.role
        )
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_lista()
        else:
            messagebox.showerror("Erro", msg)

    def excluir_produto(self):
        """Exclui o produto selecionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return
        item = self.tree.item(selected[0], "values")
        id_produto = item[0]

        confirm = messagebox.askyesno("Confirmação", f"Deseja excluir o produto ID {id_produto}?")
        if not confirm:
            return

        ok, msg = ProdutoController.excluir_produto(id_produto, executor=self.executor, role=self.role)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_lista()
        else:
            messagebox.showerror("Erro", msg)
