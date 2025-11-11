# APP/ui/vendas_ui.py
import flet as ft
from datetime import datetime
from typing import Optional
from APP.models.vendas_models import Venda
from APP.models.produtos_models import Produto
from APP.core.logger import logger
from APP.ui import style


class VendasUI:
    """Tela de controle de vendas (Flet)."""

    def __init__(self, page: ft.Page, voltar_callback=None, vendedor: Optional[str] = None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.vendedor = vendedor
        self.build_ui()
        logger.info("Tela de vendas carregada.")

    def build_ui(self):
        self.page.clean()
        self.page.title = "Controle de Vendas"
        self.page.bgcolor = style.BACKGROUND

        # === Título ===
        title = ft.Text(
            "💰 Registro de Vendas",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_PRIMARY,
        )

        # === Campos ===
        self.produto_dropdown = ft.Dropdown(
            label="Produto",
            options=self._carregar_produtos(),
            width=320,
            bgcolor=style.SURFACE_ALT,
            border_radius=8,
            border_color=style.BORDER,
            focused_border_color=style.ACCENT,
            color=style.TEXT_PRIMARY,
            text_style=ft.TextStyle(color=style.TEXT_PRIMARY),
            label_style=ft.TextStyle(color=style.TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=style.TEXT_SECONDARY),
        )

        self.quantidade_field = style.apply_textfield_style(
            ft.TextField(
                label="Quantidade",
                width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        )

        self.total_label = ft.Text(
            "Total: R$ 0,00",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_PRIMARY,
        )

        self.message = ft.Text("", color=style.TEXT_SECONDARY)

        # === Botões ===
        btn_calcular = style.primary_button(
            "Calcular Total",
            icon=ft.Icons.CALCULATE_OUTLINED,
            on_click=self.calcular_total,
        )
        btn_registrar = style.primary_button(
            "Registrar Venda",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            on_click=self.registrar_venda,
        )
        btn_voltar = style.ghost_button(
            "Voltar",
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            on_click=lambda e: self.voltar_callback() if callable(self.voltar_callback) else None,
        )

        # === Tabela ===
        self.tabela_vendas = style.stylize_datatable(
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Produto")),
                    ft.DataColumn(ft.Text("Quantidade")),
                    ft.DataColumn(ft.Text("Total (R$)")),
                    ft.DataColumn(ft.Text("Vendedor")),
                    ft.DataColumn(ft.Text("Data/Hora")),
                ],
                rows=[],
            )
        )

        self.atualizar_tabela()

        # === Layout ===
        layout = ft.Column(
            [
                title,
                ft.Row(
                    [self.produto_dropdown, self.quantidade_field, btn_calcular],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                    wrap=True,
                ),
                self.total_label,
                self.message,
                ft.Row(
                    [btn_registrar, btn_voltar],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                ft.Divider(color=style.DIVIDER),
                ft.Text(
                    "📜 Histórico de Vendas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=style.TEXT_PRIMARY,
                ),
                self.tabela_vendas,
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

    # ==================================================
    # === FUNÇÕES ======================================
    # ==================================================
    def _carregar_produtos(self):
        """Carrega produtos cadastrados para o dropdown."""
        try:
            produtos = Produto.listar()
            return [ft.dropdown.Option(p[1]) for p in produtos]
        except Exception as err:
            logger.error(f"Erro ao carregar produtos: {err}")
            return []

    def calcular_total(self, e):
        """Calcula o total da venda."""
        try:
            produto_nome = self.produto_dropdown.value
            qtd = int(self.quantidade_field.value or 0)

            if not produto_nome:
                self.message.value = "Selecione um produto."
                self.message.color = style.ERROR
                self.page.update()
                return

            if qtd <= 0:
                self.message.value = "Quantidade inválida."
                self.message.color = style.ERROR
                self.page.update()
                return

            preco = Produto.obter_preco(produto_nome)
            total = preco * qtd
            self.total_label.value = f"Total: R$ {total:.2f}"
            self.total = total
            self.message.value = ""
            self.page.update()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = style.ERROR
            logger.error(f"Erro ao calcular total: {err}")
            self.page.update()

    def registrar_venda(self, e):
        """Registra uma nova venda no banco."""
        try:
            produto_nome = self.produto_dropdown.value
            qtd = int(self.quantidade_field.value or 0)

            if not produto_nome or qtd <= 0:
                self.message.value = "Preencha os campos corretamente!"
                self.page.update()
                return

            preco = Produto.obter_preco(produto_nome)
            total = preco * qtd

            vendedor = self.vendedor or "N/D"
            Venda.registrar(produto_nome, qtd, total, vendedor)
            self.message.value = f"Venda registrada com sucesso! ({produto_nome})"
            self.message.color = style.SUCCESS
            logger.info(f"Venda registrada: {produto_nome} x{qtd} = R${total:.2f} por {vendedor}")

            # Atualiza tabela
            self.atualizar_tabela()

            # Limpa campos
            self.produto_dropdown.value = None
            self.quantidade_field.value = ""
            self.total_label.value = "Total: R$ 0,00"

            self.page.update()

        except Exception as err:
            self.message.value = f"Erro ao registrar venda: {err}"
            self.message.color = style.ERROR
            logger.error(f"Erro ao registrar venda: {err}")
            self.page.update()

    def atualizar_tabela(self):
        """Atualiza a tabela de vendas."""
        try:
            vendas = Venda.listar()
            self.tabela_vendas.rows = []
            for v in vendas:
                # Converter data/hora para formato brasileiro
                try:
                    data_formatada = datetime.strptime(v[5], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                except Exception:
                    data_formatada = v[5] or "-"

                self.tabela_vendas.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(v[0]), color=style.TEXT_SECONDARY)),
                            ft.DataCell(ft.Text(v[1], color=style.TEXT_PRIMARY)),
                            ft.DataCell(ft.Text(str(v[2]), color=style.TEXT_SECONDARY)),
                            ft.DataCell(ft.Text(f"R$ {v[3]:.2f}", color=style.TEXT_SECONDARY)),
                            ft.DataCell(ft.Text(v[4] or "N/D", color=style.TEXT_SECONDARY)),
                            ft.DataCell(ft.Text(data_formatada, color=style.TEXT_SECONDARY)),
                        ]
                    )
                )
            self.page.update()
        except Exception as err:
            logger.error(f"Erro ao atualizar tabela de vendas: {err}")
            self.message.value = f"Erro: {err}"
            self.message.color = style.ERROR
            self.page.update()
