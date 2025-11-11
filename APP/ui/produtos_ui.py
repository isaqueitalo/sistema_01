# APP/ui/produtos_ui.py
import flet as ft
from APP.models.produtos_models import Produto
from APP.core.logger import logger
from APP.ui import style


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
        self.page.bgcolor = style.BACKGROUND

        title = ft.Text(
            "📦 Controle de Produtos",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_PRIMARY,
        )

        # === Campos de formulário ===
        self.nome_field = style.apply_textfield_style(
            ft.TextField(label="Nome do produto", width=320)
        )
        self.preco_field = style.apply_textfield_style(
            ft.TextField(
                label="Preço (R$)",
                width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        )
        self.estoque_field = style.apply_textfield_style(
            ft.TextField(
                label="Estoque",
                width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        )
        self.fornecedor_field = style.apply_textfield_style(
            ft.TextField(
                label="Fornecedor",
                width=320,
                hint_text="Digite o fornecedor (opcional)",
            )
        )
        self.validade_field = style.apply_textfield_style(
            ft.TextField(
                label="Validade (AAAA-MM-DD)",
                width=220,
                hint_text="Opcional",
            )
        )

        # === Campo de busca ===
        self.busca_field = style.apply_textfield_style(
            ft.TextField(
                label="🔍 Pesquisar produto...",
                width=320,
                on_change=self.filtrar_produtos,
                hint_text="Digite parte do nome",
            )
        )

        self.message = ft.Text("", color=style.TEXT_SECONDARY)

        # === Botões ===
        btn_add = style.primary_button("Adicionar", icon=ft.Icons.ADD_ROUNDED, on_click=self.adicionar_produto)
        btn_update = style.primary_button(
            "Atualizar",
            icon=ft.Icons.SAVE_OUTLINED,
            on_click=self.atualizar_produto,
        )
        btn_delete = style.danger_button(
            "Excluir",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=self.excluir_produto,
        )
        btn_voltar = style.ghost_button(
            "Voltar",
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            on_click=lambda e: self.voltar_callback() if callable(self.voltar_callback) else None,
        )

        # === Tabela ===
        self.tabela = style.stylize_datatable(
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Nome")),
                    ft.DataColumn(ft.Text("Preço")),
                    ft.DataColumn(ft.Text("Estoque")),
                    ft.DataColumn(ft.Text("Fornecedor")),
                    ft.DataColumn(ft.Text("Validade")),
                ],
                rows=[],
                width=760,
            )
        )

        # === Layout principal ===
        layout = ft.Column(
            [
                title,
                ft.Row(
                    [self.nome_field, self.preco_field, self.estoque_field],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    wrap=True,
                ),
                ft.Row(
                    [self.fornecedor_field, self.validade_field],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    wrap=True,
                ),
                ft.Row(
                    [btn_add, btn_update, btn_delete, btn_voltar],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    wrap=True,
                ),
                self.message,
                ft.Divider(color=style.DIVIDER),
                ft.Row([self.busca_field], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(
                    "📋 Lista de Produtos",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=style.TEXT_PRIMARY,
                ),
                self.tabela,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.add(
            ft.Container(
                content=style.surface_container(layout, padding=28),
                padding=ft.Padding(24, 24, 24, 24),
                expand=True,
                alignment=ft.alignment.center,
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
            self.message.color = style.ERROR
            logger.error(f"Erro ao listar produtos: {err}")
        self.page.update()

    def _render_tabela(self, produtos):
        """Renderiza a tabela a partir de uma lista de produtos."""
        self.tabela.rows = []
        for p in produtos:
            self.tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p[0]), color=style.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(p[1], color=style.TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(f"R$ {p[2]:.2f}", color=style.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(str(p[3]), color=style.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(p[4] if p[4] else "-", color=style.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(p[5] if p[5] else "-", color=style.TEXT_SECONDARY)),
                    ],
                    on_select_changed=lambda e, nome=p[1]: self._preencher_formulario(nome),
                )
            )
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
            self.message.color = style.SUCCESS
            logger.info(f"Produto '{nome}' adicionado.")
            self.atualizar_tabela()
            self._limpar_campos()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = style.ERROR
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
            self.message.color = style.SUCCESS
            logger.info(f"Produto '{nome}' atualizado.")
            self.atualizar_tabela()
            self._limpar_campos()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = style.ERROR
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
            self.message.color = style.SUCCESS
            logger.info(f"Produto '{nome}' excluído.")
            self.atualizar_tabela()
            self._limpar_campos()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = style.ERROR
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
