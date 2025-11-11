# APP/ui/vendas_ui.py
import flet as ft
from datetime import datetime
from typing import Optional
from APP.models.vendas_models import Venda
from APP.models.produtos_models import Produto
from APP.core.logger import logger


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

        # === Título ===
        title = ft.Text("💰 Registro de Vendas", size=22, weight=ft.FontWeight.BOLD)

        # === Campos ===
        self.produto_dropdown = ft.Dropdown(
            label="Produto",
            options=self._carregar_produtos(),
            width=300,
        )

        self.quantidade_field = ft.TextField(
            label="Quantidade",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.total_label = ft.Text("Total: R$ 0,00", size=16, weight=ft.FontWeight.BOLD)

        self.message = ft.Text("", color=ft.Colors.RED_400)

        # === Botões ===
        btn_calcular = ft.ElevatedButton("Calcular Total", on_click=self.calcular_total)
        btn_registrar = ft.ElevatedButton("Registrar Venda", on_click=self.registrar_venda)
        btn_voltar = ft.TextButton("Voltar", on_click=lambda e: self.voltar_callback())

        # === Tabela ===
        self.tabela_vendas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Produto")),
                ft.DataColumn(ft.Text("Quantidade")),
                ft.DataColumn(ft.Text("Total (R$)")),
                ft.DataColumn(ft.Text("Vendedor")),
                ft.DataColumn(ft.Text("Data/Hora")),
            ],
            rows=[]
        )

        self.atualizar_tabela()

        # === Layout ===
        self.page.add(
            ft.Column(
                [
                    title,
                    ft.Row([self.produto_dropdown, self.quantidade_field, btn_calcular]),
                    self.total_label,
                    self.message,
                    ft.Row([btn_registrar, btn_voltar], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(),
                    ft.Text("📜 Histórico de Vendas", size=18, weight=ft.FontWeight.BOLD),
                    self.tabela_vendas,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
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
                self.page.update()
                return

            if qtd <= 0:
                self.message.value = "Quantidade inválida."
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
            self.message.color = ft.Colors.GREEN_400
            logger.info(f"Venda registrada: {produto_nome} x{qtd} = R${total:.2f}")

            # Atualiza tabela
            self.atualizar_tabela()

            # Limpa campos
            self.produto_dropdown.value = None
            self.quantidade_field.value = ""
            self.total_label.value = "Total: R$ 0,00"

            self.page.update()

        except Exception as err:
            self.message.value = f"Erro ao registrar venda: {err}"
            self.message.color = ft.Colors.RED_400
            logger.info(f"Venda registrada: {produto_nome} x{qtd} = R${total:.2f} por {vendedor}")
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
                            ft.DataCell(ft.Text(str(v[0]))),
                            ft.DataCell(ft.Text(v[1])),
                            ft.DataCell(ft.Text(str(v[2]))),
                            ft.DataCell(ft.Text(f"R$ {v[3]:.2f}")),
                            ft.DataCell(ft.Text(v[4] or "N/D")),
                            ft.DataCell(ft.Text(data_formatada)),
                        ]
                    )
                )
            self.page.update()
        except Exception as err:
            logger.error(f"Erro ao atualizar tabela de vendas: {err}")
            self.message.value = f"Erro: {err}"
            self.page.update()
