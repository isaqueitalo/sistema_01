import flet as ft
from typing import Optional, List, Dict
from datetime import datetime
import uuid
from APP.models.vendas_models import Venda
from APP.models.produtos_models import Produto
from APP.core.logger import logger
from APP.ui import style


class VendasUI:
    """PDV inspirado no SIGE Lite com etapas, atalhos de teclado e formas de pagamento."""

    def __init__(self, page: ft.Page, voltar_callback=None, vendedor: Optional[str] = None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.vendedor = vendedor or "N/D"

        self.cart: List[Dict] = []
        self.desconto_percent = 0.0
        self.forma_pagamento: Optional[str] = None
        self.stage_order = ["nova", "pagamento", "finalizar"]
        self.stage = "nova"
        self.pending_confirm = None
        self.pending_cancel = None
        self.sugestoes_container = None
        self.sugestoes_list = None
        self.sugestoes_data: List[Dict] = []
        self.sugestao_index = -1
        self._skip_next_codigo_submit = False
        self._dialog_id = None
        self.pedido_id = self._gerar_pedido_id()
        self.pedido_label = ft.Text(self._pedido_label_text(), color=style.TEXT_SECONDARY)
        self.focusable_controls: List[Dict] = []
        self.focus_index = -1
        self.ultima_venda_resumo = None

        self.pagamentos_def = [
            {"label": "Dinheiro", "shortcut": "F1", "color": "#22C55E", "icon": ft.Icons.ATTACH_MONEY},
            {"label": "Cheque", "shortcut": "F2", "color": "#F97316", "icon": ft.Icons.RECEIPT_LONG},
            {"label": "Cartão Crédito", "shortcut": "F3", "color": "#EC4899", "icon": ft.Icons.CREDIT_CARD},
            {"label": "Cartão Débito", "shortcut": "F4", "color": "#6366F1", "icon": ft.Icons.CREDIT_SCORE},
            {"label": "PIX", "shortcut": "F5", "color": "#0EA5E9", "icon": ft.Icons.QR_CODE_2},
            {"label": "Vale Alimentação", "shortcut": "F6", "color": "#FACC15", "icon": ft.Icons.LUNCH_DINING},
            {"label": "Vale Presente", "shortcut": "F7", "color": "#14B8A6", "icon": ft.Icons.CARD_GIFTCARD},
            {"label": "Outros", "shortcut": "F9", "color": "#EAB308", "icon": ft.Icons.MORE_HORIZ},
        ]
        self.payment_shortcuts = {opt["shortcut"]: opt for opt in self.pagamentos_def}

        self._prev_keyboard_handler = None

        self.build_ui()
        self._install_keyboard_handler()
        logger.info("Tela de vendas PDV carregada.")

    # ==================================================
    # UI
    # ==================================================
    def build_ui(self):
        self._reset_focusable_controls()
        self.page.clean()
        self.page.title = "PDV - Nova venda"
        self.page.bgcolor = style.BACKGROUND
        self.page.scroll = ft.ScrollMode.AUTO

        header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("SIGE Lite • PDV", size=24, weight=ft.FontWeight.BOLD, color=style.TEXT_PRIMARY),
                                ft.Text(f"Operador: {self.vendedor}", color=style.TEXT_SECONDARY),
                                self.pedido_label,
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        style.ghost_button("Voltar (F11)", icon=ft.Icons.ARROW_BACK, on_click=self._voltar),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(color=style.DIVIDER),
            ],
            spacing=8,
        )

        self.stepper_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=40)
        self._update_stepper()

        self.codigo_field = style.apply_textfield_style(
            ft.TextField(
                label="Código / leitura de barras",
                width=500,
                autofocus=True,
                on_submit=self._processar_codigo,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_500, color=style.TEXT_DARK),
            ),
            variant="light",
        )
        self.codigo_field.on_change = self._atualizar_sugestoes

        self.quantidade_field = style.apply_textfield_style(
            ft.TextField(
                label="Qtd (F4)",
                width=130,
                keyboard_type=ft.KeyboardType.NUMBER,
                value="1",
                on_submit=self._processar_codigo,
            ),
            variant="light",
        )

        add_button = style.primary_button("Adicionar produto (F3)", icon=ft.Icons.ADD_SHOPPING_CART, on_click=self._processar_codigo)

        self.cliente_field = style.apply_textfield_style(
            ft.TextField(
                label="Cliente (F7)",
                width=320,
                value="Consumidor Final",
                on_change=lambda _: self._atualizar_cliente_resumo(),
            ),
            variant="light",
        )

        self.alert_text = ft.Text("", color=style.ERROR)
        self.sugestoes_list = ft.Column(spacing=4, tight=True)
        self.sugestoes_container = ft.Container(
            content=self.sugestoes_list,
            bgcolor=style.PANEL_MUTED,
            padding=ft.Padding(12, 10, 12, 10),
            border_radius=10,
            width=500,
            visible=False,
        )

        self.tabela = style.stylize_datatable(
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nº")),
                    ft.DataColumn(ft.Text("Produto")),
                    ft.DataColumn(ft.Text("Quantidade (F4)")),
                    ft.DataColumn(ft.Text("Valor Unit. (F5)")),
                    ft.DataColumn(ft.Text("Valor Total")),
                    ft.DataColumn(ft.Text("Ações")),
                ],
                rows=[],
            ),
            header_bg=style.PANEL_MUTED,
            variant="light",
        )

        self.payment_grid = ft.ResponsiveRow(spacing=12, run_spacing=12)
        self._render_pagamentos()

        shortcut_entries = [
            (
                style.flat_shortcut_button(
                    "Buscar produto",
                    "F2",
                    icon=ft.Icons.SEARCH,
                    on_click=lambda _: self._focus_codigo(),
                    width=130,
                ),
                lambda: self._focus_codigo(),
            ),
            (
                style.flat_shortcut_button(
                    "Adicionar produto",
                    "F3",
                    icon=ft.Icons.ADD,
                    on_click=self._processar_codigo,
                    width=130,
                ),
                lambda: self._processar_codigo(None),
            ),
            (
                style.flat_shortcut_button(
                    "Editar quantidade",
                    "F4",
                    icon=ft.Icons.EXPOSURE,
                    on_click=lambda _: self.quantidade_field.focus(),
                    width=130,
                ),
                lambda: self.quantidade_field.focus(),
            ),
            (
                style.flat_shortcut_button(
                    "Alterar valor",
                    "F5",
                    icon=ft.Icons.PRICE_CHANGE,
                    on_click=self._abrir_modal_valor,
                    width=130,
                ),
                lambda: self._abrir_modal_valor(None),
            ),
            (
                style.flat_shortcut_button(
                    "Remover item",
                    "F6",
                    icon=ft.Icons.DELETE_SWEEP,
                    on_click=lambda _: self._remover_last_item(),
                    width=130,
                ),
                lambda: self._remover_last_item(),
            ),
            (
                style.flat_shortcut_button(
                    "Cliente",
                    "F7",
                    icon=ft.Icons.BADGE,
                    on_click=lambda _: self.cliente_field.focus(),
                    width=130,
                ),
                lambda: self.cliente_field.focus(),
            ),
            (
                style.flat_shortcut_button(
                    "Forma de pagamento",
                    "F9",
                    icon=ft.Icons.PAYMENTS,
                    on_click=lambda _: self._set_stage("pagamento"),
                    width=130,
                ),
                lambda: self._set_stage("pagamento"),
            ),
            (
                style.flat_shortcut_button(
                    "Desconto",
                    "F10",
                    icon=ft.Icons.MONEY_OFF,
                    on_click=self._abrir_modal_desconto,
                    width=130,
                ),
                lambda: self._abrir_modal_desconto(None),
            ),
            (
                style.flat_shortcut_button(
                    "Finalizar",
                    "F8",
                    icon=ft.Icons.CHECK_CIRCLE,
                    on_click=self._finalizar_venda,
                    width=130,
                ),
                lambda: self._finalizar_venda(None),
            ),
        ]
        shortcuts = ft.ResponsiveRow(
            [entry[0] for entry in shortcut_entries],
            run_spacing=12,
            spacing=12,
        )
        for control, callback in shortcut_entries:
            self._register_focusable_control(
                control,
                callback,
                category="shortcuts",
                highlight_target=getattr(control, "content", control),
            )

        self.resumo_status = style.summary_card("Status SEFAZ", "Operante", subtitle="F12 • Operações", accent=style.SUCCESS)
        self.resumo_cliente = style.summary_card("Cliente", "Consumidor Final", subtitle="F7 • Editar", accent=style.ACCENT)
        self.resumo_pagamento = style.summary_card("Pagamento", "Selecione (F1-F7)", subtitle="F9 • Etapa", accent=style.ACCENT)
        self.resumo_itens = style.summary_card("Itens", "0", subtitle="No carrinho", accent=style.TEXT_DARK)
        self.resumo_desconto = style.summary_card("Desconto (F10)", "R$ 0,00", subtitle="", accent=style.TEXT_DARK)
        self.resumo_total = style.summary_card("Total", "R$ 0,00", subtitle="", accent=style.ACCENT)

        for card in [
            self.resumo_status,
            self.resumo_cliente,
            self.resumo_pagamento,
            self.resumo_itens,
            self.resumo_desconto,
            self.resumo_total,
        ]:
            card.col = {"xs": 12, "sm": 6, "md": 4, "lg": 2}

        self._resumo_cliente_value = self.resumo_cliente.content.controls[1]
        self._resumo_pagamento_value = self.resumo_pagamento.content.controls[1]
        self._resumo_itens_value = self.resumo_itens.content.controls[1]
        self._resumo_desconto_value = self.resumo_desconto.content.controls[1]
        self._resumo_total_value = self.resumo_total.content.controls[1]

        summary_row = ft.ResponsiveRow(
            [
                self.resumo_status,
                self.resumo_cliente,
                self.resumo_pagamento,
                self.resumo_itens,
                self.resumo_desconto,
                self.resumo_total,
            ],
            spacing=16,
            run_spacing=16,
        )
        self.resumo_venda_container = ft.Container(
            visible=False,
            bgcolor=style.PANEL_MUTED,
            border_radius=12,
            padding=ft.Padding(16, 14, 16, 14),
        )

        self.finalizar_btn = style.primary_button(
            "Finalizar venda (F8)",
            icon=ft.Icons.POINT_OF_SALE,
            on_click=self._finalizar_venda,
            bgcolor=style.SUCCESS,
        )
        finalizar_wrapper = ft.Container(content=self.finalizar_btn, border_radius=12)
        self._register_focusable_control(
            finalizar_wrapper,
            lambda: self._finalizar_venda(None),
            category="primary",
            highlight_target=finalizar_wrapper,
        )

        captura_section = style.surface_container(
            ft.Column(
                [
                    ft.Row(
                        [self.codigo_field, self.quantidade_field, add_button],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    self.sugestoes_container,
                    self.cliente_field,
                    self.alert_text,
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor=style.PANEL_LIGHT,
        )

        self.tabela_container = ft.Container(
            content=self.tabela,
            bgcolor=style.PANEL_MUTED,
            border_radius=12,
            padding=ft.Padding(12, 12, 12, 12),
            height=220,
        )
        carrinho_section = style.surface_container(
            ft.Column(
                [
                    ft.Text("Carrinho de itens", weight=ft.FontWeight.W_600, color=style.TEXT_DARK),
                    self.tabela_container,
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor=style.PANEL_LIGHT,
        )

        shortcuts_section = style.surface_container(
            ft.Column(
                [
                    ft.Text("Ações rápidas", weight=ft.FontWeight.W_600, color=style.TEXT_DARK),
                    shortcuts,
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor=style.PANEL_LIGHT,
        )

        pagamento_section = style.surface_container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Formas de pagamento", size=18, weight=ft.FontWeight.W_600, color=style.TEXT_DARK),
                            ft.Text(
                                "Use F1-F7 ou clique para selecionar.",
                                color=style.TEXT_MUTED,
                                size=12,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.payment_grid,
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor=style.PANEL_LIGHT,
        )

        resumo_section = style.surface_container(
            ft.Column(
                [
                    summary_row,
                    self.resumo_venda_container,
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor=style.PANEL_LIGHT,
        )

        finalizar_section = style.surface_container(
            ft.Column(
                [
                    ft.Text("Etapa final", weight=ft.FontWeight.W_600, color=style.TEXT_DARK),
                    finalizar_wrapper,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=14,
            bgcolor=style.PANEL_LIGHT,
        )

        layout = ft.Column(
            [
                header,
                self.stepper_row,
                captura_section,
                carrinho_section,
                shortcuts_section,
                pagamento_section,
                resumo_section,
                finalizar_section,
            ],
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
        )

        self.page.add(
            ft.Container(
                content=style.surface_container(layout, padding=28, bgcolor=style.PANEL_LIGHT),
                padding=ft.Padding(24, 24, 24, 24),
                expand=True,
                alignment=ft.alignment.center,
            )
        )
        self._atualizar_resumo()
        self._focus_codigo()

    # ==================================================
    # LÓGICA DE CARRINHO
    # ==================================================
    def _processar_codigo(self, _):
        if self._skip_next_codigo_submit:
            self._skip_next_codigo_submit = False
            return
        codigo = (self.codigo_field.value or "").strip()
        quantidade = self._obter_quantidade_digitada()

        if self.sugestoes_data:
            if self.sugestao_index < 0:
                self.sugestao_index = 0
            produto_info = self.sugestoes_data[self.sugestao_index]["produto"]
            self._limpar_sugestoes()
            self._mostrar_confirmacao_produto(produto_info, quantidade)
            return

        if not codigo:
            self._set_alert("Informe o código ou nome do produto.")
            return

        produto = Produto.buscar_por_codigo_ou_nome(codigo)
        if not produto:
            sugestoes = Produto.buscar_sugestoes(codigo, limit=1)
            if sugestoes:
                produto_dict = self._produto_row_to_dict(sugestoes[0])
                self._limpar_sugestoes()
                self._mostrar_confirmacao_produto(produto_dict, quantidade)
                return
            self._set_alert("Produto não encontrado.")
            return

        produto_dict = {
            "id": int(produto[0]),
            "nome": produto[1],
            "preco": float(produto[2]),
            "estoque": int(produto[3]),
            "codigo": produto[4],
        }
        self._limpar_sugestoes()
        self._mostrar_confirmacao_produto(produto_dict, quantidade)

    def _mostrar_confirmacao_produto(self, produto_info: Dict, quantidade: int):
        nome = produto_info["nome"]
        preco = produto_info["preco"]
        estoque = produto_info["estoque"]
        codigo = produto_info["codigo"]
        total = preco * quantidade

        conteudo = ft.Column(
            [
                ft.Text(f"{nome}", size=18, weight=ft.FontWeight.BOLD, color=style.TEXT_DARK),
                ft.Text(f"Código: {codigo or '-'} • Estoque disponível: {estoque}", color=style.TEXT_MUTED),
                ft.Text(f"Quantidade: {quantidade}", color=style.TEXT_DARK),
                ft.Text(f"Valor unitário: R$ {preco:.2f}", color=style.TEXT_MUTED),
                ft.Text(f"Total: R$ {total:.2f}", weight=ft.FontWeight.BOLD, color=style.ACCENT),
            ],
            spacing=4,
        )

        def confirmar(_):
            self._fechar_dialogo()
            self.pending_confirm = None
            self.pending_cancel = None
            self._adicionar_ao_carrinho(produto_info, quantidade)
            self.codigo_field.value = ""
            self.quantidade_field.value = "1"
            self._set_alert("")
            self._set_stage("nova")
            self._focus_codigo()
            self._limpar_sugestoes()
            self.page.update()

        def cancelar(_):
            self._fechar_dialogo()
            self.pending_confirm = None
            self.pending_cancel = None
            self._set_alert("Produto cancelado.")
            self._focus_codigo()
            self._limpar_sugestoes()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Adicionar produto"),
            content=conteudo,
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                style.primary_button(
                    "Confirmar",
                    icon=ft.Icons.CHECK,
                    on_click=confirmar,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.pending_confirm = confirmar
        self.pending_cancel = cancelar
        self._abrir_dialogo(dialog, "confirmar_produto")

    def _adicionar_ao_carrinho(self, produto_info: Dict, quantidade: int = 1):
        produto_id = produto_info["id"]
        nome = produto_info["nome"]
        preco = produto_info["preco"]
        codigo = produto_info["codigo"]
        if quantidade <= 0:
            quantidade = 1

        existente = next((item for item in self.cart if item["id"] == produto_id), None)
        if existente:
            existente["quantidade"] += quantidade
        else:
            self.cart.append(
                {
                    "id": produto_id,
                    "nome": nome,
                    "valor_unitario": float(preco),
                    "quantidade": quantidade,
                    "codigo": codigo,
                }
            )
        self._atualizar_tabela()
        logger.info("Carrinho: %s x%d adicionado (total itens=%d)", nome, quantidade, len(self.cart))
        self._mostrar_snackbar(f"{nome} x{quantidade} adicionado ao carrinho")
        self._focus_codigo()

    def _atualizar_tabela(self):
        rows: List[ft.DataRow] = []
        for idx, item in enumerate(self.cart, start=1):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(idx), color=style.TEXT_DARK)),
                        ft.DataCell(ft.Text(item["nome"], color=style.TEXT_DARK)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                        icon_color=style.ERROR,
                                        on_click=self._make_alterar_quantidade_handler(item["id"], -1),
                                    ),
                                    ft.Text(str(item["quantidade"]), color=style.TEXT_DARK),
                                    ft.IconButton(
                                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                        icon_color=style.SUCCESS,
                                        on_click=self._make_alterar_quantidade_handler(item["id"], 1),
                                    ),
                                ],
                                spacing=4,
                            )
                        ),
                        ft.DataCell(ft.Text(f"R$ {item['valor_unitario']:.2f}", color=style.TEXT_DARK)),
                        ft.DataCell(ft.Text(f"R$ {item['valor_unitario'] * item['quantidade']:.2f}", color=style.TEXT_DARK)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=style.ERROR,
                                tooltip="Remover (F6)",
                                on_click=self._make_remover_handler(item["id"]),
                            )
                        ),
                    ]
                )
            )
        self.tabela.rows = rows
        self._atualizar_resumo()
        self.tabela.update()
        self.page.update()

    def _make_alterar_quantidade_handler(self, produto_id: int, delta: int):
        def handler(_):
            self._alterar_quantidade(produto_id, delta)
        return handler

    def _make_remover_handler(self, produto_id: int):
        def handler(_):
            self._remover_item(produto_id)
        return handler

    def _alterar_quantidade(self, produto_id: int, delta: int):
        for item in self.cart:
            if item["id"] == produto_id:
                item["quantidade"] = max(1, item["quantidade"] + delta)
                break
        self._atualizar_tabela()

    def _remover_item(self, produto_id: int):
        self.cart = [item for item in self.cart if item["id"] != produto_id]
        self._atualizar_tabela()

    def _remover_last_item(self):
        if self.cart:
            self.cart.pop()
            self._atualizar_tabela()

    def _atualizar_resumo(self):
        total_itens = sum(item["quantidade"] for item in self.cart)
        total_bruto = sum(item["quantidade"] * item["valor_unitario"] for item in self.cart)
        desconto_valor = total_bruto * (self.desconto_percent / 100)
        total_liquido = total_bruto - desconto_valor

        self._resumo_itens_value.value = str(total_itens)
        self._resumo_desconto_value.value = f"R$ {desconto_valor:.2f}"
        self._resumo_total_value.value = f"R$ {total_liquido:.2f}"
        self._resumo_cliente_value.value = self.cliente_field.value or "Consumidor Final"
        self._resumo_pagamento_value.value = self.forma_pagamento or "Selecione (F1-F7)"
        self.page.update()

    def _validar_venda_pronta(self):
        if not self.cart:
            return False, "Adicione itens antes de finalizar.", None
        if not self.forma_pagamento:
            return False, "Selecione uma forma de pagamento (F1-F7).", None

        cliente = (self.cliente_field.value or "Consumidor Final").strip() or "Consumidor Final"
        total_bruto = sum(item["quantidade"] * item["valor_unitario"] for item in self.cart)
        desconto_valor = total_bruto * (self.desconto_percent / 100)
        total_liquido = total_bruto - desconto_valor
        return True, "", (total_bruto, desconto_valor, total_liquido, cliente)

    def _on_pagamento_select(self, shortcut: str):
        option = self.payment_shortcuts.get(shortcut)
        if not option:
            return
        self.forma_pagamento = option["label"]
        self._set_stage("finalizar")
        self._render_pagamentos()
        self._atualizar_resumo()
        self.page.update()

    def _render_pagamentos(self):
        tiles = []
        self._remove_focusable_category("payment")
        for opt in self.pagamentos_def:
            tile = style.flat_shortcut_button(
                opt["label"],
                opt["shortcut"],
                icon=opt["icon"],
                color=opt["color"],
                on_click=lambda _, shortcut=opt["shortcut"]: self._on_pagamento_select(shortcut),
                selected=self.forma_pagamento == opt["label"],
                width=150,
                col={"xs": 6, "sm": 4, "md": 3, "lg": 2},
            )
            tiles.append(tile)
            self._register_focusable_control(
                tile,
                lambda shortcut=opt["shortcut"]: self._on_pagamento_select(shortcut),
                category="payment",
                highlight_target=getattr(tile, "content", tile),
            )
        self.payment_grid.controls = tiles
        self.page.update()
        if self.forma_pagamento:
            self._focus_finalizar()

    def _executar_finalizacao(self, cliente, total_liquido, itens_snapshot: List[Dict]):
        try:
            logger.debug(
                "Executando finalização: itens=%d | pagamento=%s | cliente=%s",
                len(itens_snapshot),
                self.forma_pagamento or "N/D",
                cliente,
            )
            for item in itens_snapshot:
                Venda.registrar(
                    item["nome"],
                    item["quantidade"],
                    item["quantidade"] * item["valor_unitario"],
                    vendedor=self.vendedor,
                    cliente=cliente,
                    forma_pagamento=self.forma_pagamento,
                    pedido_id=self.pedido_id,
                )
            logger.info(
                "Venda finalizada por %s | itens=%d | pagamento=%s | cliente=%s | total=%.2f",
                self.vendedor,
                len(self.cart),
                self.forma_pagamento,
                cliente,
                total_liquido,
            )
            self._fechar_dialogo()
            self._mostrar_snackbar(f"Venda registrada: R$ {total_liquido:.2f}")
            self.cart.clear()
            self.desconto_percent = 0.0
            self.forma_pagamento = None
            self._set_stage("nova")
            self._render_pagamentos()
            self._resetar_formulario_pos_venda()
            logger.debug("Venda finalizada: carrinho limpo e UI pronta para nova operação.")
        except Exception as err:
            logger.error("Erro ao finalizar venda: %s", err, exc_info=True)
            self._mostrar_snackbar(f"Erro ao finalizar: {err}", erro=True)

    def _atualizar_cliente_resumo(self):
        self._resumo_cliente_value.value = self.cliente_field.value or "Consumidor Final"
        self.page.update()

    # ==================================================
    # MODAIS
    # ==================================================
    def _abrir_modal_desconto(self, _):
        campo = style.apply_textfield_style(
            ft.TextField(label="Percentual de desconto", value=str(self.desconto_percent), keyboard_type=ft.KeyboardType.NUMBER),
            variant="light",
        )

        def salvar(_):
            try:
                self.desconto_percent = max(0.0, float(campo.value or 0))
                self._atualizar_resumo()
                self._fechar_dialogo()
            except ValueError:
                campo.error_text = "Valor inválido"
                self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Aplicar desconto (F10)"),
            content=campo,
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo),
                style.primary_button("Aplicar", icon=ft.Icons.CHECK, on_click=salvar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._abrir_dialogo(dialog, "modal_desconto")

    def _abrir_modal_valor(self, _):
        if not self.cart:
            self._mostrar_snackbar("Nenhum item para alterar valor.", erro=True)
            return
        item = self.cart[-1]
        campo = style.apply_textfield_style(
            ft.TextField(label=f"Valor unitário de {item['nome']}", value=str(item["valor_unitario"]), keyboard_type=ft.KeyboardType.NUMBER),
            variant="light",
        )

        def salvar(_):
            try:
                item["valor_unitario"] = float(campo.value)
                self._atualizar_tabela()
                self._fechar_dialogo()
            except ValueError:
                campo.error_text = "Valor inválido"
                self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Alterar valor (F5)"),
            content=campo,
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo),
                style.primary_button("Aplicar", icon=ft.Icons.SAVE, on_click=salvar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._abrir_dialogo(dialog, "modal_valor")

    def _abrir_dialogo(self, dialog: ft.AlertDialog, dialog_id: str):
        try:
            current_dialog = self.page.dialog
        except AttributeError:
            current_dialog = None
        if current_dialog:
            current_dialog.open = False
            self.page.update()
        try:
            self.page.dialog = dialog
        except AttributeError:
            logger.error("Não foi possível atribuir dialog à página.")
            return
        dialog.open = True
        self.page.update()
        self._dialog_id = dialog_id
        logger.debug("Diálogo aberto: %s", dialog_id)

    def _fechar_dialogo(self, _=None):
        try:
            current_dialog = self.page.dialog
        except AttributeError:
            current_dialog = None
        if current_dialog:
            current_dialog.open = False
            self.page.update()
            try:
                self.page.dialog = None
            except AttributeError:
                pass
            logger.debug("Diálogo fechado: %s", getattr(self, "_dialog_id", "desconhecido"))
        self._dialog_id = None

    # ==================================================
    # FINALIZAÇÃO
    # ==================================================
    def _finalizar_venda(self, _):
        logger.debug(
            "Finalizar solicitado: itens=%d | pagamento=%s",
            len(self.cart),
            self.forma_pagamento or "N/D",
        )
        if self.pending_confirm or self.pending_cancel:
            logger.debug("Cancelando diálogo pendente antes da finalização.")
            self.pending_confirm = None
            self.pending_cancel = None
            self._fechar_dialogo()
        ok, msg, totals = self._validar_venda_pronta()
        if not ok:
            logger.warning(
                "Validação da venda falhou: %s | itens=%d | pagamento=%s",
                msg,
                len(self.cart),
                self.forma_pagamento or "N/D",
            )
            self._set_alert(msg)
            self._mostrar_snackbar(msg, erro=True)
            if msg.startswith("Selecione"):
                self._set_stage("pagamento")
            else:
                self._focus_codigo()
            return

        total_bruto, desconto_valor, total_liquido, cliente = totals
        logger.debug(
            "Validação OK: total_bruto=%.2f | desconto=%.2f | total_liquido=%.2f | cliente=%s",
            total_bruto,
            desconto_valor,
            total_liquido,
            cliente,
        )
        itens_snapshot = [item.copy() for item in self.cart]
        forma_pagamento = self.forma_pagamento
        pedido_atual = self.pedido_id
        data_venda = datetime.now().strftime("%d/%m/%Y %H:%M")
        self._executar_finalizacao(cliente, total_liquido, itens_snapshot)
        self._mostrar_resumo_final(
            {
                "pedido_id": pedido_atual,
                "cliente": cliente,
                "vendedor": self.vendedor,
                "pagamento": forma_pagamento,
                "total_bruto": total_bruto,
                "desconto": desconto_valor,
                "total_liquido": total_liquido,
                "data": data_venda,
                "itens": itens_snapshot,
            }
        )

    # ==================================================
    # ETAPAS E TECLADO
    # ==================================================
    def _install_keyboard_handler(self):
        self._prev_keyboard_handler = self.page.on_keyboard_event
        self.page.on_keyboard_event = self._handle_keyboard

    def _handle_keyboard(self, e: ft.KeyboardEvent):
        key_raw = (e.key or "").upper()
        if not key_raw:
            return
        key = key_raw.replace(" ", "")

        if self.pending_confirm:
            if key == "ENTER":
                self.pending_confirm(None)
                return
            if key in ("ESCAPE", "F6"):
                if self.pending_cancel:
                    self.pending_cancel(None)
                return

        if self.sugestoes_data:
            if key in ("ARROWDOWN", "DOWN", "TAB"):
                self._mover_sugestao(1)
                return
            if key in ("ARROWUP", "UP"):
                self._mover_sugestao(-1)
                return
            if key == "ENTER":
                self._skip_next_codigo_submit = True
                self._selecionar_sugestao()
                return
            if key == "ESCAPE":
                self._limpar_sugestoes()
                return

        if key in self.payment_shortcuts:
            if self.stage != "pagamento":
                self._set_stage("pagamento")
            self._on_pagamento_select(key)
            return
        if key in ("ARROWRIGHT", "RIGHT", "D"):
            if self._move_focus(1):
                return
        if key in ("ARROWLEFT", "LEFT", "A"):
            if self._move_focus(-1):
                return
        if key in ("ARROWDOWN", "DOWN", "S"):
            if self._move_focus(1):
                return
        if key in ("ARROWUP", "UP", "W"):
            if self._move_focus(-1):
                return

        if self.stage == "pagamento":
            if key in ("ESCAPE", "F9"):
                self._set_stage("nova")
                return

        if key in ("ENTER", "SPACE"):
            if self._activate_focused_control():
                return
        if key == "ENTER":
            self._processar_codigo(None)
        elif key == "F2":
            self._focus_codigo()
        elif key == "F3":
            self._processar_codigo(None)
        elif key == "F4":
            self.quantidade_field.focus()
        elif key == "F5":
            self._abrir_modal_valor(None)
        elif key == "F6":
            self._remover_last_item()
        elif key == "F7":
            self.cliente_field.focus()
        elif key == "F8":
            self._finalizar_venda(None)
        elif key == "F9":
            self._set_stage("pagamento" if self.stage != "pagamento" else "nova")
        elif key == "F10":
            self._abrir_modal_desconto(None)
        elif key == "F11":
            self._voltar()

    def _set_stage(self, stage: str):
        if stage not in self.stage_order:
            return
        self.stage = stage
        self._update_stepper()
        self.page.update()

    def _update_stepper(self):
        labels = [("nova", "Nova venda"), ("pagamento", "Forma de pagamento"), ("finalizar", "Finalizar")]
        current_index = self.stage_order.index(self.stage)
        chips = []
        for idx, (key, label) in enumerate(labels):
            state = "done" if idx < current_index else "active" if idx == current_index else "pending"
            chips.append(self._step_chip(label, state))
        self.stepper_row.controls = chips

    def _step_chip(self, label: str, state: str) -> ft.Row:
        if state == "done":
            color = style.SUCCESS
        elif state == "active":
            color = style.ACCENT
        else:
            color = style.TEXT_SECONDARY

        return ft.Row(
            [
                ft.Container(
                    width=14,
                    height=14,
                    border_radius=20,
                    bgcolor=color,
                ),
                ft.Text(label, color=color, weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    # ==================================================
    # UTILITÁRIOS
    # ==================================================
    def _focus_codigo(self):
        self.codigo_field.focus()
        self.page.update()

    def _focus_finalizar(self):
        for idx, entry in enumerate(self.focusable_controls):
            ctrl = entry.get("control")
            if isinstance(ctrl, ft.Container) and getattr(ctrl, "content", None) is getattr(self, "finalizar_btn", None):
                self.focus_index = idx
                self._update_focusable_highlight()
                return

    def _resetar_formulario_pos_venda(self):
        """Prepara os campos para uma nova venda após concluir a anterior."""
        if self.codigo_field:
            self.codigo_field.value = ""
        if self.quantidade_field:
            self.quantidade_field.value = "1"
        if self.cliente_field:
            self.cliente_field.value = "Consumidor Final"
            self._atualizar_cliente_resumo()
        self.cart.clear()
        self._atualizar_tabela()
        self.forma_pagamento = None
        self._render_pagamentos()
        self._set_alert("")
        self._limpar_sugestoes()
        self._focus_codigo()
        self._novo_pedido()

    def _set_alert(self, texto: str):
        self.alert_text.value = texto
        self.page.update()

    def _obter_quantidade_digitada(self) -> int:
        try:
            qtd = int(self.quantidade_field.value or "1")
            return max(1, qtd)
        except ValueError:
            return 1

    def _produto_row_to_dict(self, row):
        return {
            "id": int(row[0]),
            "nome": row[1],
            "preco": float(row[2]),
            "estoque": int(row[3]),
            "codigo": row[4],
        }

    def _gerar_pedido_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:4].upper()
        return f"{timestamp}-{suffix}"

    def _pedido_label_text(self) -> str:
        return f"Pedido atual: #{self.pedido_id}"

    def _novo_pedido(self):
        self.pedido_id = self._gerar_pedido_id()
        if self.pedido_label:
            self.pedido_label.value = self._pedido_label_text()
        if self.page:
            self.page.update()

    def _reset_focusable_controls(self):
        for entry in getattr(self, "focusable_controls", []):
            self._apply_focus_highlight(entry, False)
        self.focusable_controls = []
        self.focus_index = -1

    def _register_focusable_control(self, control, activate_callback, *, category="default", highlight_target=None):
        if control is None:
            return
        target = highlight_target or getattr(control, "content", control)
        entry = {
            "control": control,
            "target": target,
            "activate": activate_callback,
            "category": category,
            "default_border": getattr(target, "border", None),
        }
        self.focusable_controls.append(entry)
        self._update_focusable_highlight()

    def _remove_focusable_category(self, category: str):
        remaining = []
        for entry in self.focusable_controls:
            if entry["category"] == category:
                self._apply_focus_highlight(entry, False)
            else:
                remaining.append(entry)
        self.focusable_controls = remaining
        if self.focus_index >= len(self.focusable_controls):
            self.focus_index = len(self.focusable_controls) - 1
        self._update_focusable_highlight()

    def _apply_focus_highlight(self, entry, active: bool):
        target = entry["target"]
        if hasattr(target, "border"):
            target.border = ft.border.all(2, style.ACCENT) if active else entry["default_border"]
        if active:
            self._scroll_target_into_view(target)

    def _update_focusable_highlight(self):
        for idx, entry in enumerate(self.focusable_controls):
            self._apply_focus_highlight(entry, idx == self.focus_index and self.focus_index >= 0)
        if self.page:
            self.page.update()

    def _scroll_target_into_view(self, target):
        scroll_fn = getattr(target, "scroll_into_view", None)
        if callable(scroll_fn):
            try:
                scroll_fn(alignment=0.4)
                return
            except Exception:
                pass
        page_scroll = getattr(self.page, "scroll_to", None)
        if callable(page_scroll):
            try:
                page_scroll(control=target, duration=200)
            except Exception:
                pass

    def _move_focus(self, delta: int) -> bool:
        if not self.focusable_controls:
            return False
        if self.focus_index == -1:
            self.focus_index = 0 if delta > 0 else len(self.focusable_controls) - 1
        else:
            self.focus_index = (self.focus_index + delta) % len(self.focusable_controls)
        self._update_focusable_highlight()
        return True

    def _activate_focused_control(self) -> bool:
        if self.focus_index < 0 or self.focus_index >= len(self.focusable_controls):
            return False
        entry = self.focusable_controls[self.focus_index]
        if callable(entry["activate"]):
            entry["activate"]()
            return True
        return False

    def _atualizar_sugestoes(self, e=None):
        if e is not None and hasattr(e, "data") and e.data is not None:
            termo = e.data.strip()
        elif e is not None and getattr(e, "control", None) is not None:
            termo = (e.control.value or "").strip()
        else:
            termo = (self.codigo_field.value or "").strip()
        if not termo:
            self._limpar_sugestoes()
            return

        sugestoes = Produto.buscar_sugestoes(termo, limit=6)
        if not sugestoes:
            self._limpar_sugestoes()
            return

        qtd = self._obter_quantidade_digitada()
        items = []
        self.sugestoes_data = []
        for row in sugestoes:
            produto = self._produto_row_to_dict(row)
            item = ft.Container(
                bgcolor=style.PANEL_LIGHT,
                border_radius=8,
                padding=ft.Padding(10, 6, 10, 6),
                ink=True,
                on_click=lambda _, info=produto: self._selecionar_sugestao(info),
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(produto["nome"], weight=ft.FontWeight.BOLD, color=style.TEXT_DARK),
                                ft.Text(f"Código: {produto['codigo'] or '-'}", color=style.TEXT_MUTED, size=12),
                            ],
                            spacing=0,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {produto['preco']:.2f}", color=style.ACCENT),
                    ]
                ),
            )
            items.append(item)
            self.sugestoes_data.append({"produto": produto, "control": item})

        self.sugestoes_list.controls = items
        self.sugestao_index = 0 if items else -1
        self._atualizar_destaque_sugestoes()
        self.sugestoes_container.visible = True
        self.page.update()

    def _limpar_sugestoes(self):
        self.sugestoes_data = []
        self.sugestao_index = -1
        if self.sugestoes_list:
            self.sugestoes_list.controls = []
        if self.sugestoes_container:
            self.sugestoes_container.visible = False
        if self.page:
            self.page.update()

    def _atualizar_destaque_sugestoes(self):
        for idx, data in enumerate(self.sugestoes_data):
            ctrl = data["control"]
            selecionado = idx == self.sugestao_index
            ctrl.bgcolor = style.ACCENT if selecionado else style.PANEL_LIGHT
            coluna = ctrl.content.controls[0]
            preco_text = ctrl.content.controls[2]
            coluna.controls[0].color = style.TEXT_PRIMARY if selecionado else style.TEXT_DARK
            coluna.controls[1].color = style.TEXT_SECONDARY if selecionado else style.TEXT_MUTED
            preco_text.color = style.TEXT_PRIMARY if selecionado else style.ACCENT
        self.page.update()

    def _mover_sugestao(self, delta: int):
        if not self.sugestoes_data:
            return
        self.sugestao_index = (self.sugestao_index + delta) % len(self.sugestoes_data)
        self._atualizar_destaque_sugestoes()

    def _selecionar_sugestao(self, produto=None):
        if produto is None:
            if not self.sugestoes_data:
                return
            if self.sugestao_index < 0:
                self.sugestao_index = 0
            produto = self.sugestoes_data[self.sugestao_index]["produto"]
        self._limpar_sugestoes()
        self._mostrar_confirmacao_produto(produto, self._obter_quantidade_digitada())

    def _mostrar_snackbar(self, texto, erro=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=style.ERROR if erro else style.SURFACE,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _mostrar_resumo_final(self, resumo: Dict):
        self.ultima_venda_resumo = resumo
        if not self.resumo_venda_container:
            return
        itens_column = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(item["nome"], color=style.TEXT_DARK),
                        ft.Text(
                            f"x{item['quantidade']} • R$ {item['valor_unitario'] * item['quantidade']:.2f}",
                            color=style.TEXT_SECONDARY,
                            size=12,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                for item in resumo.get("itens", [])
            ],
            spacing=2,
        )
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"Venda finalizada • Pedido #{resumo['pedido_id']}",
                            weight=ft.FontWeight.BOLD,
                            color=style.TEXT_DARK,
                        ),
                        ft.Text(resumo["data"], color=style.TEXT_MUTED, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    f"Cliente: {resumo['cliente']} | Pagamento: {resumo['pagamento']} | Vendedor: {resumo['vendedor']}",
                    color=style.TEXT_SECONDARY,
                    size=12,
                ),
                itens_column,
                ft.Row(
                    [
                        ft.Text(
                            f"Total bruto: R$ {resumo['total_bruto']:.2f}",
                            color=style.TEXT_MUTED,
                        ),
                        ft.Text(
                            f"Desconto: R$ {resumo['desconto']:.2f}",
                            color=style.TEXT_MUTED,
                        ),
                        ft.Text(
                            f"Total pago: R$ {resumo['total_liquido']:.2f}",
                            weight=ft.FontWeight.BOLD,
                            color=style.ACCENT,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=6,
        )
        self.resumo_venda_container.content = content
        self.resumo_venda_container.visible = True
        self.page.update()

    def _voltar(self, _=None):
        self._restore_keyboard_handler()
        if callable(self.voltar_callback):
            self.page.clean()
            self.voltar_callback()

    def _restore_keyboard_handler(self):
        self.page.on_keyboard_event = self._prev_keyboard_handler

