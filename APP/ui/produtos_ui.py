# APP/ui/produtos_ui.py
import flet as ft
from APP.models.produtos_models import Produto
from APP.core.logger import logger


class ProdutosUI:
    """Tela moderna e minimalista de gerenciamento de produtos (com busca dinâmica)."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.produtos_cache = []  # cache para busca
        self.build_ui()
        logger.info("Tela de produtos carregada.")

    # ======================================================
    # === INTERFACE =======================================
    # ======================================================

    def build_ui(self):
        self.page.clean()
        self.page.title = "Gerenciamento de Produtos"

        title = ft.Text("📦 Controle de Produtos", size=22, weight=ft.FontWeight.BOLD)

        # === Campos de formulário ===
        self.nome_field = ft.TextField(label="Nome do produto", width=300)
        self.preco_field = ft.TextField(label="Preço (R$)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.estoque_field = ft.TextField(label="Estoque", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.fornecedor_field = ft.TextField(label="Fornecedor", width=300)
        self.validade_field = ft.TextField(label="Validade (AAAA-MM-DD)", width=200, hint_text="Opcional")
        
        # === Campo de busca ===
        self.busca_field = ft.TextField(
            label="🔍 Pesquisar produto...",
            width=300,
            on_change=self.filtrar_produtos,
            hint_text="Digite parte do nome",
        )

        self.message = ft.Text("", color=ft.Colors.RED_400)

        # === Botões ===
        btn_add = ft.ElevatedButton("Adicionar", on_click=self.adicionar_produto)
        btn_update = ft.ElevatedButton("Atualizar", on_click=self.atualizar_produto)
        btn_delete = ft.ElevatedButton("Excluir", on_click=self.excluir_produto)
        btn_voltar = ft.TextButton("Voltar", on_click=lambda e: self.voltar_callback())

        # === Tabela ===
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Preço")),
                ft.DataColumn(ft.Text("Estoque")),
                ft.DataColumn(ft.Text("Fornecedor")),
                ft.DataColumn(ft.Text("Validade")),
            ],
            rows=[],
            width=700
        )

        # === Layout principal ===
        self.page.add(
            ft.Column(
                [
                    title,
                    ft.Row([self.nome_field, self.preco_field, self.estoque_field]),
                    ft.Row([self.fornecedor_field, self.validade_field], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([btn_add, btn_update, btn_delete, btn_voltar], alignment=ft.MainAxisAlignment.CENTER),
                    self.message,
                    ft.Divider(),
                    ft.Row([self.busca_field], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("📋 Lista de Produtos", size=18, weight=ft.FontWeight.BOLD),
                    self.tabela,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            )
        )

        self.atualizar_tabela()

    # ======================================================
    # === FUNÇÕES ==========================================
    # ======================================================

    def atualizar_tabela(self):
        """Carrega todos os produtos e atualiza tabela."""
        try:
            produtos = Produto.listar()
            self.produtos_cache = produtos  # salva em cache para busca
            self._render_tabela(produtos)
        except Exception as err:
            self.message.value = f"Erro ao carregar produtos: {err}"
            self.message.color = ft.Colors.RED_400
            logger.error(f"Erro ao listar produtos: {err}")
        self.page.update()

    def _render_tabela(self, produtos):
        """Renderiza a tabela a partir de uma lista de produtos."""
        self.tabela.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(p[0]))),
                    ft.DataCell(ft.Text(p[1])),
                    ft.DataCell(ft.Text(f"R$ {p[2]:.2f}")),
                    ft.DataCell(ft.Text(str(p[3]))),
                    ft.DataCell(ft.Text(p[4] if p[4] else "-")),
                    ft.DataCell(ft.Text(p[5] if p[5] else "-")),
                ],
                on_select_changed=lambda e, nome=p[1]: self._preencher_formulario(nome),
            )
            for p in produtos
        ]
        self.page.update()

    def filtrar_produtos(self, e):
        """Filtra produtos em tempo real conforme o texto digitado."""
        termo = self.busca_field.value.strip().lower()
        if not termo:
            self._render_tabela(self.produtos_cache)
            return

        filtrados = [p for p in self.produtos_cache if termo in p[1].lower()]
        self._render_tabela(filtrados)

    def _preencher_formulario(self, nome_produto):
        """Preenche os campos ao clicar em um item da tabela."""
        try:
            produto = next((p for p in self.produtos_cache if p[1] == nome_produto), None)
            if produto:
                self.nome_field.value = produto[1]
                self.preco_field.value = str(produto[2])
                self.estoque_field.value = str(produto[3])
                self.fornecedor_field.value = produto[4] or ""
                self.validade_field.value = produto[5] or ""
                self.page.update()
        except Exception as err:
            logger.error(f"Erro ao preencher formulário: {err}")

    def adicionar_produto(self, e):
        """Adiciona um novo produto ao banco."""
        nome = self.nome_field.value.strip()
        preco = self.preco_field.value.strip()
        estoque = self.estoque_field.value.strip()
        fornecedor = self.fornecedor_field.value.strip()
        validade = self.validade_field.value.strip()


        if not nome or not preco or not estoque:
            self.message.value = "Informe nome, preço e estoque!"
            self.page.update()
            return

        try:
            preco = float(preco)
            estoque = int(estoque)
            fornecedor = fornecedor or None
            validade = validade or None
            Produto.adicionar(nome, preco, estoque, fornecedor, validade)
            self.message.value = f"✅ Produto '{nome}' adicionado com sucesso!"
            self.message.color = ft.Colors.GREEN_400
            logger.info(f"Produto '{nome}' adicionado.")
            self.atualizar_tabela()
            self._limpar_campos()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = ft.Colors.RED_400
            logger.error(f"Erro ao adicionar produto: {err}")
        self.page.update()

    def atualizar_produto(self, e):
        """Atualiza um produto existente."""
        nome = self.nome_field.value.strip()
        preco = self.preco_field.value.strip()
        estoque = self.estoque_field.value.strip()
        fornecedor = self.fornecedor_field.value.strip()
        validade = self.validade_field.value.strip()

        if not nome:
            self.message.value = "Digite o nome do produto a atualizar!"
            self.page.update()
            return

        try:
            preco = float(preco) if preco else None
            estoque = int(estoque) if estoque else None
            fornecedor = fornecedor if fornecedor else None
            validade = validade if validade else None
            Produto.atualizar(nome, preco, estoque, fornecedor, validade)
            self.message.value = f"🔁 Produto '{nome}' atualizado com sucesso!"
            self.message.color = ft.Colors.GREEN_400
            logger.info(f"Produto '{nome}' atualizado.")
            self.atualizar_tabela()
            self._limpar_campos()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = ft.Colors.RED_400
            logger.error(f"Erro ao atualizar produto: {err}")
        self.page.update()

    def excluir_produto(self, e):
        """Exclui um produto pelo nome."""
        nome = self.nome_field.value.strip()

        if not nome:
            self.message.value = "Digite o nome do produto a excluir!"
            self.page.update()
            return

        try:
            Produto.excluir(nome)
            self.message.value = f"🗑️ Produto '{nome}' excluído!"
            self.message.color = ft.Colors.GREEN_400
            logger.info(f"Produto '{nome}' excluído.")
            self.atualizar_tabela()
            self._limpar_campos()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = ft.Colors.RED_400
            logger.error(f"Erro ao excluir produto: {err}")
        self.page.update()

    def _limpar_campos(self):
        """Limpa os campos do formulário."""
        self.nome_field.value = ""
        self.preco_field.value = ""
        self.estoque_field.value = ""
        self.fornecedor_field.value = ""
        self.validade_field.value = ""
        self.page.update()
        self.page.update()
