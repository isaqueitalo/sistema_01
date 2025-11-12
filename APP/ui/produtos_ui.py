import flet as ft
from APP.models.produtos_models import Produto
from APP.models.categorias_models import Categoria
from APP.models.unidades_models import UnidadeMedida
from APP.core.logger import logger
from APP.ui import style


class ProdutosUI:
    """Tela moderna e minimalista de gerenciamento de produtos (com busca dinâmica)."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.produtos_cache = []
        self.categorias_cache = []
        self.unidades_cache = []
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
            color=style.TEXT_DARK,
        )

        dropdown_style = dict(
            width=260,
            bgcolor=style.SURFACE_ALT,
            border_radius=8,
            border_color=style.BORDER,
            focused_border_color=style.ACCENT,
            color=style.TEXT_PRIMARY,
            label_style=ft.TextStyle(color=style.TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=style.TEXT_SECONDARY),
        )

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
        self.categoria_dropdown = ft.Dropdown(
            label="Categoria",
            options=[],
            **dropdown_style,
        )
        self.unidade_dropdown = ft.Dropdown(
            label="Unidade",
            options=[],
            **dropdown_style,
        )
        self.codigo_barras_field = style.apply_textfield_style(
            ft.TextField(
                label="Código de barras",
                width=220,
                hint_text="Opcional",
            )
        )
        self.estoque_minimo_field = style.apply_textfield_style(
            ft.TextField(
                label="Estoque mínimo",
                width=160,
                keyboard_type=ft.KeyboardType.NUMBER,
                hint_text="0",
            )
        )
        self.localizacao_field = style.apply_textfield_style(
            ft.TextField(
                label="Localização no estoque",
                width=220,
                hint_text="Ex.: Prateleira A",
            )
        )

        self._atualizar_dropdown_categorias()
        self._atualizar_dropdown_unidades()

        self.busca_field = style.apply_textfield_style(
            ft.TextField(
                label="🔎 Pesquisar produto...",
                width=320,
                on_change=self.filtrar_produtos,
                hint_text="Digite parte do nome",
            )
        )

        self.message = ft.Text("", color=style.TEXT_MUTED)

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
        btn_new_categoria = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="Nova categoria",
            icon_color=style.ACCENT,
            on_click=self._abrir_dialogo_categoria,
        )
        btn_new_unidade = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="Nova unidade",
            icon_color=style.ACCENT,
            on_click=self._abrir_dialogo_unidade,
        )

        self.tabela = style.stylize_datatable(
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Nome")),
                    ft.DataColumn(ft.Text("Categoria")),
                    ft.DataColumn(ft.Text("Unidade")),
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Preço")),
                    ft.DataColumn(ft.Text("Estoque")),
                    ft.DataColumn(ft.Text("Estoque mín.")),
                    ft.DataColumn(ft.Text("Fornecedor")),
                    ft.DataColumn(ft.Text("Validade")),
                    ft.DataColumn(ft.Text("Localização")),
                ],
                rows=[],
                width=1000,
            )
        )

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
                    [
                        ft.Row(
                            [self.categoria_dropdown, btn_new_categoria],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [self.unidade_dropdown, btn_new_unidade],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=24,
                    wrap=True,
                ),
                ft.Row(
                    [self.codigo_barras_field, self.estoque_minimo_field, self.localizacao_field],
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
                    color=style.TEXT_DARK,
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
    # === FUNÇÕES =========================================
    # ======================================================
    def atualizar_tabela(self):
        """Carrega todos os produtos e atualiza tabela."""
        try:
            produtos = Produto.listar()
            self.produtos_cache = produtos
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
            categoria = p[6] or "-"
            unidade = p[7] or "-"
            codigo = p[8] or "-"
            estoque_min = p[9] if p[9] is not None else "-"
            localizacao = p[10] or "-"
            self.tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p[0]), color=style.TEXT_MUTED)),
                        ft.DataCell(
                            ft.Text(
                                p[1],
                                color=style.TEXT_DARK,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            )
                        ),
                        ft.DataCell(ft.Text(categoria, color=style.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(unidade, color=style.TEXT_MUTED)),
                        ft.DataCell(ft.Text(codigo, color=style.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(f"R$ {p[2]:.2f}", color=style.TEXT_MUTED)),
                        ft.DataCell(ft.Text(str(p[3]), color=style.TEXT_MUTED)),
                        ft.DataCell(ft.Text(str(estoque_min), color=style.TEXT_MUTED)),
                        ft.DataCell(ft.Text(p[4] if p[4] else "-", color=style.TEXT_MUTED)),
                        ft.DataCell(ft.Text(p[5] if p[5] else "-", color=style.TEXT_MUTED)),
                        ft.DataCell(ft.Text(localizacao, color=style.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS)),
                    ],
                    on_select_changed=lambda e, produto=tuple(p): self._preencher_formulario(produto),
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

    def _preencher_formulario(self, produto):
        """Preenche os campos ao clicar em um item da tabela."""
        try:
            self.nome_field.value = produto[1]
            self.preco_field.value = str(produto[2])
            self.estoque_field.value = str(produto[3])
            self.fornecedor_field.value = produto[4] or ""
            self.validade_field.value = produto[5] or ""
            self.categoria_dropdown.value = str(produto[11]) if produto[11] else ""
            self.unidade_dropdown.value = str(produto[12]) if produto[12] else ""
            self.codigo_barras_field.value = produto[8] or ""
            self.estoque_minimo_field.value = "" if produto[9] is None else str(produto[9])
            self.localizacao_field.value = produto[10] or ""
            self.page.update()
        except Exception as err:
            logger.error(f"Erro ao preencher formulário: {err}")

    def adicionar_produto(self, e):
        """Adiciona um novo produto ao banco."""
        nome = self.nome_field.value.strip()
        preco_raw = self.preco_field.value.strip()
        estoque_raw = self.estoque_field.value.strip()
        fornecedor = self.fornecedor_field.value.strip()
        validade = self.validade_field.value.strip()
        codigo_barras = self.codigo_barras_field.value.strip() or None
        estoque_minimo_raw = self.estoque_minimo_field.value.strip()
        localizacao = self.localizacao_field.value.strip() or None

        if not nome or not preco_raw or not estoque_raw:
            self.message.value = "Informe nome, preço e estoque!"
            self.page.update()
            return

        try:
            preco = float(preco_raw)
            estoque = int(estoque_raw)
            estoque_minimo = int(estoque_minimo_raw) if estoque_minimo_raw else 0
        except ValueError:
            self.message.value = "Valores numéricos inválidos."
            self.message.color = style.ERROR
            self.page.update()
            return

        try:
            Produto.adicionar(
                nome,
                preco,
                estoque,
                fornecedor=fornecedor or None,
                validade=validade or None,
                categoria_id=self._parse_dropdown_value(self.categoria_dropdown.value),
                unidade_id=self._parse_dropdown_value(self.unidade_dropdown.value),
                codigo_barras=codigo_barras,
                estoque_minimo=estoque_minimo,
                localizacao=localizacao,
            )
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
        if not nome:
            self.message.value = "Digite o nome do produto a atualizar!"
            self.page.update()
            return

        preco_raw = self.preco_field.value.strip()
        estoque_raw = self.estoque_field.value.strip()
        fornecedor = self.fornecedor_field.value.strip()
        validade = self.validade_field.value.strip()
        codigo_barras = self.codigo_barras_field.value.strip() or None
        estoque_minimo_raw = self.estoque_minimo_field.value.strip()
        localizacao = self.localizacao_field.value.strip() or None

        payload = {
            "fornecedor": fornecedor or None,
            "validade": validade or None,
            "categoria_id": self._parse_dropdown_value(self.categoria_dropdown.value),
            "unidade_id": self._parse_dropdown_value(self.unidade_dropdown.value),
            "codigo_barras": codigo_barras,
            "estoque_minimo": int(estoque_minimo_raw) if estoque_minimo_raw else 0,
            "localizacao": localizacao,
        }

        try:
            if preco_raw:
                payload["preco"] = float(preco_raw)
            if estoque_raw:
                payload["estoque"] = int(estoque_raw)
        except ValueError:
            self.message.value = "Valores numéricos inválidos."
            self.message.color = style.ERROR
            self.page.update()
            return

        try:
            Produto.atualizar(nome, **payload)
            self.message.value = f"💾 Produto '{nome}' atualizado com sucesso!"
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
        self.categoria_dropdown.value = ""
        self.unidade_dropdown.value = ""
        self.codigo_barras_field.value = ""
        self.estoque_minimo_field.value = ""
        self.localizacao_field.value = ""
        self.page.update()

    # ======================================================
    # === AUXILIARES ======================================
    # ======================================================
    def _parse_dropdown_value(self, value):
        return int(value) if value not in (None, "", "None") else None

    def _atualizar_dropdown_categorias(self, select_id=None):
        try:
            self.categorias_cache = list(Categoria.listar())
        except Exception as err:
            logger.error(f"Erro ao carregar categorias: {err}")
            self.categorias_cache = []

        options = [ft.dropdown.Option("", "Sem categoria")]
        options.extend(
            ft.dropdown.Option(str(cat["id"]), cat["nome"])
            for cat in self.categorias_cache
        )
        self.categoria_dropdown.options = options
        if select_id is not None:
            self.categoria_dropdown.value = str(select_id)
        elif self.categoria_dropdown.value is None:
            self.categoria_dropdown.value = ""
        self.page.update()

    def _atualizar_dropdown_unidades(self, select_id=None):
        try:
            self.unidades_cache = list(UnidadeMedida.listar())
        except Exception as err:
            logger.error(f"Erro ao carregar unidades: {err}")
            self.unidades_cache = []

        options = [ft.dropdown.Option("", "Sem unidade")]
        options.extend(
            ft.dropdown.Option(str(uni["id"]), f"{uni['sigla']} - {uni['descricao']}")
            for uni in self.unidades_cache
        )
        self.unidade_dropdown.options = options
        if select_id is not None:
            self.unidade_dropdown.value = str(select_id)
        elif self.unidade_dropdown.value is None:
            self.unidade_dropdown.value = ""
        self.page.update()

    def _abrir_dialogo_categoria(self, e):
        nome_field = style.apply_textfield_style(ft.TextField(label="Nome da categoria", width=300))
        segmento_field = style.apply_textfield_style(
            ft.TextField(label="Segmento (farmácia, padaria...)", value="geral", width=300)
        )

        def salvar(_):
            try:
                categoria_id = Categoria.adicionar(nome_field.value, segmento_field.value)
                self._fechar_dialogo()
                self._atualizar_dropdown_categorias(select_id=categoria_id)
                self._mostrar_snackbar("Categoria criada com sucesso.")
            except Exception as err:
                self._mostrar_snackbar(f"Erro: {err}", erro=True)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova categoria"),
            content=ft.Column(
                [nome_field, segmento_field],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo),
                style.primary_button("Salvar", icon=ft.Icons.SAVE_ROUNDED, on_click=salvar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _abrir_dialogo_unidade(self, e):
        sigla_field = style.apply_textfield_style(
            ft.TextField(label="Sigla (UN, KG...)", width=200, text_capitalization=ft.TextCapitalization.CHARACTERS)
        )
        descricao_field = style.apply_textfield_style(
            ft.TextField(label="Descrição", width=300, hint_text="Opcional")
        )

        def salvar(_):
            try:
                unidade_id = UnidadeMedida.adicionar(sigla_field.value, descricao_field.value)
                self._fechar_dialogo()
                self._atualizar_dropdown_unidades(select_id=unidade_id)
                self._mostrar_snackbar("Unidade cadastrada com sucesso.")
            except Exception as err:
                self._mostrar_snackbar(f"Erro: {err}", erro=True)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova unidade"),
            content=ft.Column(
                [sigla_field, descricao_field],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo),
                style.primary_button("Salvar", icon=ft.Icons.SAVE_ROUNDED, on_click=salvar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _fechar_dialogo(self, e=None):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _mostrar_snackbar(self, texto, erro=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=style.ERROR if erro else style.SURFACE_ALT,
        )
        self.page.snack_bar.open = True
        self.page.update()
