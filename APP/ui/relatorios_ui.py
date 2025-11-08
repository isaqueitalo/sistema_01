import flet as ft
import io
import os
import base64
import platform
import subprocess
import matplotlib
matplotlib.use("Agg")  # ✅ Evita aviso de GUI fora da main thread
import matplotlib.pyplot as plt
from datetime import datetime
from fpdf import FPDF
from APP.models.vendas_models import Venda
from APP.core.logger import logger


class RelatoriosUI:
    """Tela de relatórios e estatísticas de vendas com exportação em PDF."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.vendas_atual = []
        self.graficos_binarios = []
        self.ultimo_pdf = None  # Guarda o caminho do último PDF gerado
        self.build_ui()

    def build_ui(self):
        self.page.clean()
        self.page.title = "Relatórios de Vendas"

        hoje = datetime.now().strftime("%d/%m/%Y")

        # Campos de data
        self.data_inicio = ft.TextField(
            label="Data Início (DD/MM/YYYY)",
            value=hoje,
            width=200,
            keyboard_type=ft.KeyboardType.DATETIME,
        )
        self.data_fim = ft.TextField(
            label="Data Fim (DD/MM/YYYY)",
            value=hoje,
            width=200,
            keyboard_type=ft.KeyboardType.DATETIME,
        )

        gerar_btn = ft.ElevatedButton("🔍 Gerar Relatório", on_click=self.gerar_relatorio)
        exportar_btn = ft.ElevatedButton("📄 Exportar PDF", on_click=self.exportar_pdf)
        abrir_pasta_btn = ft.OutlinedButton("📂 Abrir Pasta", on_click=self.abrir_pasta)
        voltar_btn = ft.OutlinedButton("← Voltar", on_click=lambda e: self.voltar_callback())

        self.resumo_text = ft.Text(
            "Selecione um período e clique em 'Gerar Relatório'.",
            size=16,
            weight=ft.FontWeight.BOLD,
        )

        self.graficos = ft.Row(spacing=20, wrap=True, alignment=ft.MainAxisAlignment.CENTER)

        self.page.add(
            ft.Column(
                [
                    ft.Text("📊 Relatórios de Vendas", size=22, weight=ft.FontWeight.BOLD),
                    ft.Row([self.data_inicio, self.data_fim, gerar_btn, exportar_btn, abrir_pasta_btn, voltar_btn]),
                    ft.Divider(),
                    self.resumo_text,
                    ft.Divider(),
                    self.graficos,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            )
        )

        logger.info("Tela de relatórios com PDF e botão de pasta carregada.")
        self.page.update()

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

        if not vendas:
            self.resumo_text.value = f"⚠️ Nenhuma venda encontrada entre {self.data_inicio.value} e {self.data_fim.value}."
            self.page.update()
            return

        total_vendas = len(vendas)
        total_valor = sum(v[3] for v in vendas)
        self.resumo_text.value = f"🧾 Total de vendas: {total_vendas} | 💵 Valor total: R$ {total_valor:.2f}"

        produtos = {}
        for v in vendas:
            produtos[v[1]] = produtos.get(v[1], 0) + v[2]

        # === Gráfico de Barras ===
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        ax1.bar(produtos.keys(), produtos.values(), color="#4A90E2")
        ax1.set_title("Vendas por Produto", fontsize=12, weight="bold")
        ax1.set_xlabel("Produto")
        ax1.set_ylabel("Quantidade")
        ax1.grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="png")
        plt.close(fig1)
        buf1.seek(0)
        img1_bytes = buf1.getvalue()
        self.graficos_binarios.append(img1_bytes)

        # === Gráfico de Pizza ===
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.pie(
            produtos.values(),
            labels=produtos.keys(),
            autopct="%1.1f%%",
            colors=["#6FA8DC", "#93C47D", "#FFD966", "#E06666", "#8E7CC3"],
        )
        ax2.set_title("Participação nas Vendas", fontsize=12, weight="bold")
        plt.tight_layout()

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png")
        plt.close(fig2)
        buf2.seek(0)
        img2_bytes = buf2.getvalue()
        self.graficos_binarios.append(img2_bytes)

        # === Exibe na tela ===
        img1 = ft.Image(src_base64=base64.b64encode(img1_bytes).decode(), width=380, height=280)
        img2 = ft.Image(src_base64=base64.b64encode(img2_bytes).decode(), width=380, height=280)
        self.graficos.controls.extend([img1, img2])

        logger.info(f"Relatório gerado de {data_inicio} a {data_fim}.")
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

            total_valor = sum(v[3] for v in self.vendas_atual)
            total_vendas = len(self.vendas_atual)
            pdf.cell(0, 10, f"Total de vendas: {total_vendas}", ln=True)
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
            for v in self.vendas_atual:
                data_formatada = datetime.strptime(v[4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                pdf.cell(0, 8, f"#{v[0]} | {v[1]} x{v[2]} | R$ {v[3]:.2f} | {data_formatada}", ln=True)

            # Salva arquivo
            filename = f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            self.ultimo_pdf = os.path.abspath(filename)
            logger.info(f"PDF gerado: {self.ultimo_pdf}")

            self.page.snack_bar = ft.SnackBar(ft.Text(f"✅ Relatório exportado: {filename}"))
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
