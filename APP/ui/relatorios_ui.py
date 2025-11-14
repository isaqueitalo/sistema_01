import flet as ft
import io
import os
import base64
import platform
import subprocess
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # ✅ Evita aviso de GUI fora da main thread
import matplotlib.pyplot as plt
plt.style.use("dark_background")
from datetime import datetime
from fpdf import FPDF
from APP.models.vendas_models import Venda
from APP.core.logger import logger
from APP.ui import style


class RelatoriosUI:
    """Tela de relatórios e estatísticas de vendas com exportação em PDF."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.vendas_atual = []
        self.graficos_binarios = []
        self.ultimo_pdf = None  # Guarda o caminho do último PDF gerado
        self.vendas_list = None
        self.build_ui()

    def build_ui(self):
        self.page.clean()
        self.page.title = "Relatórios de Vendas"
        self.page.bgcolor = style.BACKGROUND

        hoje = datetime.now().strftime("%d/%m/%Y")

        # Campos de data
        self.data_inicio = style.apply_textfield_style(
            ft.TextField(
                label="Data Início (DD/MM/YYYY)",
                value=hoje,
                width=220,
                keyboard_type=ft.KeyboardType.DATETIME,
            )
        )
        self.data_fim = style.apply_textfield_style(
            ft.TextField(
                label="Data Fim (DD/MM/YYYY)",
                value=hoje,
                width=220,
                keyboard_type=ft.KeyboardType.DATETIME,
            )
        )

        gerar_btn = style.primary_button("Gerar Relatório", icon=ft.Icons.SEARCH_ROUNDED, on_click=self.gerar_relatorio)
        exportar_btn = style.primary_button("Exportar PDF", icon=ft.Icons.PICTURE_AS_PDF_OUTLINED, on_click=self.exportar_pdf)
        abrir_pasta_btn = style.ghost_button("Abrir Pasta", icon=ft.Icons.FOLDER_OPEN, on_click=self.abrir_pasta)
        voltar_btn = style.ghost_button(
            "Voltar",
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            on_click=lambda e: self.voltar_callback() if callable(self.voltar_callback) else None,
        )

        self.resumo_text = ft.Text(
            "Selecione um período e clique em 'Gerar Relatório'.",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_DARK,
        )

        self.graficos = ft.Row(spacing=20, wrap=True, alignment=ft.MainAxisAlignment.CENTER)
        self.vendas_list = ft.ListView(spacing=10, padding=0, expand=True, auto_scroll=False)
        self.vendas_list_container = ft.Container(
            content=self.vendas_list,
            height=320,
            bgcolor=style.PANEL_MUTED,
            border_radius=12,
            padding=ft.Padding(12, 12, 12, 12),
        )

        header = ft.Text(
            "📊 Relatórios de Vendas",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_DARK,
        )

        layout = ft.Column(
            [
                header,
                ft.Row(
                    [self.data_inicio, self.data_fim, gerar_btn, exportar_btn, abrir_pasta_btn, voltar_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=14,
                    wrap=True,
                ),
                ft.Divider(color=style.DIVIDER),
                self.resumo_text,
                ft.Divider(color=style.DIVIDER),
                self.graficos,
                ft.Divider(color=style.DIVIDER),
                ft.Text(
                    "Detalhamento das vendas",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=style.TEXT_DARK,
                ),
                self.vendas_list_container,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
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

        logger.info("Tela de relatórios com PDF e botão de pasta carregada.")
        self.page.update()
        self._atualizar_detalhamento_vendas()

    # ======================================================
    # GERAÇÃO DE RELATÓRIOS
    # ======================================================
    def gerar_relatorio(self, e):
        try:
            data_inicio = datetime.strptime(self.data_inicio.value, "%d/%m/%Y").strftime("%Y-%m-%d")
            data_fim = datetime.strptime(self.data_fim.value, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ Datas inválidas. Use o formato DD/MM/YYYY."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        vendas = Venda.listar_periodo(data_inicio, data_fim)
        self.vendas_atual = vendas
        self.graficos.controls.clear()
        self.graficos_binarios.clear()
        self._atualizar_detalhamento_vendas()

        if not vendas:
            self.resumo_text.value = f"?? Nenhuma venda encontrada entre {self.data_inicio.value} e {self.data_fim.value}."
            self.resumo_text.color = style.TEXT_MUTED
            self.page.update()
            return

        total_vendas = len(vendas)
        total_valor = sum(pedido['total'] for pedido in vendas)
        self.resumo_text.value = f"?? Total de pedidos: {total_vendas} | ?? Valor total: R$ {total_valor:.2f}"
        self.resumo_text.color = style.TEXT_DARK

        produtos = {}
        for pedido in vendas:
            for item in pedido['itens']:
                produtos[item['produto']] = produtos.get(item['produto'], 0) + item['quantidade']

        # === Gráfico de Barras ===
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        fig1.patch.set_facecolor(style.SURFACE)
        ax1.set_facecolor(style.SURFACE_ALT)
        ax1.bar(produtos.keys(), produtos.values(), color=style.ACCENT)
        ax1.set_title("Vendas por Produto", fontsize=12, weight="bold", color=style.TEXT_PRIMARY)
        ax1.set_xlabel("Produto", color=style.TEXT_SECONDARY)
        ax1.set_ylabel("Quantidade", color=style.TEXT_SECONDARY)
        ax1.tick_params(colors=style.TEXT_SECONDARY, rotation=25)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(25)
            tick.set_ha("right")
        ax1.grid(axis="y", linestyle="--", alpha=0.3, color=style.TEXT_SECONDARY)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="png")
        plt.close(fig1)
        buf1.seek(0)
        img1_bytes = buf1.getvalue()
        self.graficos_binarios.append(img1_bytes)

        # === Gráfico de Pizza ===
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        fig2.patch.set_facecolor(style.SURFACE)
        colors = [style.ACCENT, "#6B9BFF", "#54C0EB", "#4ADE80", "#FBCB4A"]
        ax2.pie(
            produtos.values(),
            labels=produtos.keys(),
            autopct="%1.1f%%",
            colors=colors,
            textprops={"color": style.TEXT_PRIMARY},
        )
        ax2.set_title("Participação nas Vendas", fontsize=12, weight="bold", color=style.TEXT_PRIMARY)
        plt.tight_layout()

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png")
        plt.close(fig2)
        buf2.seek(0)
        img2_bytes = buf2.getvalue()
        self.graficos_binarios.append(img2_bytes)

        # === Exibe na tela ===
        img1 = ft.Image(src_base64=base64.b64encode(img1_bytes).decode(), width=380, height=280, border_radius=12)
        img2 = ft.Image(src_base64=base64.b64encode(img2_bytes).decode(), width=380, height=280, border_radius=12)
        self.graficos.controls.extend([img1, img2])

        logger.info(f"Relatório gerado de {data_inicio} a {data_fim}.")
        self.page.update()

    def _atualizar_detalhamento_vendas(self):
        if not self.vendas_list:
            return
        if not self.vendas_atual:
            self.vendas_list.controls = [
                ft.Text(
                    "Nenhuma venda encontrada para o período informado.",
                    color=style.TEXT_MUTED,
                )
            ]
            self.page.update()
            return

        cards = []
        for pedido in self.vendas_atual:
            venda_id = pedido["pedido_id"]
            total = pedido["total"]
            vendedor = pedido["vendedor"]
            data_raw = pedido["data_hora"]
            cliente = pedido["cliente"]
            pagamento = pedido["forma_pagamento"]

            if isinstance(data_raw, str) and data_raw.strip():
                try:
                    data_formatada = datetime.strptime(data_raw, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    data_formatada = data_raw
            else:
                data_formatada = "-"

            itens_column = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(item["produto"], color=style.TEXT_DARK, weight=ft.FontWeight.W_500),
                            ft.Text(
                                f"x{item['quantidade']} • R$ {item['total']:.2f}",
                                color=style.TEXT_SECONDARY,
                                size=12,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                    for item in pedido["itens"]
                ],
                spacing=2,
            )

            card = ft.Container(
                bgcolor=style.PANEL_LIGHT,
                border_radius=12,
                padding=ft.Padding(10, 8, 10, 8),
                border=ft.border.all(1, style.BORDER),
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT_LONG, color=style.ACCENT),
                        ft.Column(
                            [
                                ft.Text(
                                    f"Pedido #{venda_id}",
                                    weight=ft.FontWeight.BOLD,
                                    color=style.TEXT_DARK,
                                ),
                                ft.Text(
                                    f"Horário: {data_formatada}",
                                    color=style.TEXT_MUTED,
                                    size=12,
                                ),
                                itens_column,
                                ft.Text(f"Cliente: {cliente}", color=style.TEXT_SECONDARY, size=12),
                                ft.Text(f"Pagamento: {pagamento}", color=style.TEXT_SECONDARY, size=12),
                                ft.Text(f"Vendedor: {vendedor}", color=style.TEXT_SECONDARY, size=12),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Text(
                            f"R$ {total:.2f}",
                            weight=ft.FontWeight.BOLD,
                            color=style.ACCENT,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            )
            cards.append(card)

        self.vendas_list.controls = cards
        self.page.update()

    # ======================================================
    # EXPORTAÇÃO EM PDF
    # ======================================================
    def exportar_pdf(self, e):
        if not self.vendas_atual:
            self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ Gere o relatório antes de exportar!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Relatório de Vendas", ln=True, align="C")

            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Período: {self.data_inicio.value} a {self.data_fim.value}", ln=True)
            pdf.ln(5)

            total_valor = sum(pedido["total"] for pedido in self.vendas_atual)
            total_vendas = len(self.vendas_atual)
            pdf.cell(0, 10, f"Total de pedidos: {total_vendas}", ln=True)
            pdf.cell(0, 10, f"Valor total: R$ {total_valor:.2f}", ln=True)
            pdf.ln(10)

            # Adiciona gráficos
            for i, grafico_bytes in enumerate(self.graficos_binarios):
                img_path = f"temp_grafico_{i}.png"
                with open(img_path, "wb") as f:
                    f.write(grafico_bytes)
                pdf.image(img_path, x=20, w=170)
                pdf.ln(10)

            # Adiciona tabela resumida
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Resumo de Vendas:", ln=True)
            pdf.set_font("Arial", "", 11)
            for pedido in self.vendas_atual:
                data_raw = pedido["data_hora"]
                if isinstance(data_raw, str) and data_raw.strip():
                    try:
                        data_formatada = datetime.strptime(data_raw, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    except ValueError:
                        data_formatada = data_raw
                else:
                    data_formatada = "-"

                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f"Pedido #{pedido['pedido_id']} - {data_formatada}", ln=True)
                pdf.set_font("Arial", "", 11)
                pdf.cell(
                    0,
                    7,
                    f"Cliente: {pedido['cliente']} | Pagamento: {pedido['forma_pagamento']} | Vendedor: {pedido['vendedor']}",
                    ln=True,
                )
                pdf.cell(0, 7, f"Total: R$ {pedido['total']:.2f}", ln=True)
                for item in pedido["itens"]:
                    pdf.cell(0, 6, f"- {item['produto']} x{item['quantidade']} = R$ {item['total']:.2f}", ln=True)
                pdf.ln(4)
            # Salva arquivo
            downloads_dir = Path.home() / "Downloads" / "Relatorios_Sistema"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            filename = f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = downloads_dir / filename
            pdf.output(str(filepath))
            self.ultimo_pdf = str(filepath)
            logger.info(f"PDF gerado: {self.ultimo_pdf}")

            self.page.snack_bar = ft.SnackBar(ft.Text(f"✅ Relatório exportado em {filepath}"))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            logger.error(f"Erro ao exportar PDF: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erro ao gerar PDF: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    # ======================================================
    # ABRIR PASTA DO RELATÓRIO
    # ======================================================
    def abrir_pasta(self, e):
        if not self.ultimo_pdf:
            self.page.snack_bar = ft.SnackBar(ft.Text("📄 Gere e exporte um PDF primeiro!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        pasta = os.path.dirname(self.ultimo_pdf)
        try:
            if platform.system() == "Windows":
                os.startfile(pasta)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", pasta])
            else:  # Linux
                subprocess.Popen(["xdg-open", pasta])
            logger.info(f"Abrindo pasta: {pasta}")
        except Exception as ex:
            logger.error(f"Erro ao abrir pasta: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erro ao abrir pasta: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()
