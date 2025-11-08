# APP/ui/logs_viewer.py
import flet as ft
from APP.core.config import LOG_FILE
from APP.core.logger import logger


class LogsViewer:
    """Visualizador simples de logs do sistema (Flet)."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.build_ui()
        logger.info("Tela de visualização de logs carregada.")

    def build_ui(self):
        self.page.clean()
        self.page.title = "Visualizador de Logs"

        title = ft.Text("🧾 Visualizador de Logs do Sistema", size=22, weight=ft.FontWeight.BOLD)

        # Campo de exibição de logs
        self.log_area = ft.TextField(
            multiline=True,
            read_only=True,
            expand=True,
            width=800,
            height=400,
            bgcolor=ft.Colors.BLACK,
            color=ft.Colors.GREEN_ACCENT_400,
            border=ft.InputBorder.OUTLINE,
        )

        btn_refresh = ft.ElevatedButton("🔄 Atualizar Logs", on_click=self.carregar_logs)
        btn_voltar = ft.TextButton("Voltar", on_click=lambda e: self.voltar_callback())

        self.page.add(
            ft.Column(
                [
                    title,
                    ft.Row([btn_refresh, btn_voltar], alignment=ft.MainAxisAlignment.CENTER),
                    self.log_area,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

        self.carregar_logs(None)

    def carregar_logs(self, e):
        """Carrega o conteúdo do arquivo de log system.log"""
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                conteudo = f.read()
                self.log_area.value = conteudo if conteudo else "Nenhum log disponível."
        except Exception as err:
            self.log_area.value = f"Erro ao carregar logs: {err}"
            logger.error(f"Erro ao abrir arquivo de log: {err}")
        self.page.update()
