import os
import flet as ft
from APP.core.config import config
from APP.core.logger import logger
from APP.ui import style


class LogsViewer:
    """Visualizador simples do arquivo de log do sistema."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.log_path = config.log_path
        self.build_ui()
        logger.info("Tela de logs carregada.")

    def build_ui(self):
        self.page.clean()
        self.page.title = "Visualizador de Logs"
        self.page.bgcolor = style.BACKGROUND

        title = ft.Text("🪵 Visualizador de Logs", size=22, weight=ft.FontWeight.BOLD, color=style.TEXT_DARK)

        self.text_area = ft.TextField(
            multiline=True,
            read_only=True,
            width=720,
            height=420,
            border_radius=12,
            border_color=style.BORDER,
            text_size=14,
            label="Conteúdo do log",
            value=self._ler_logs(),
            color=style.TEXT_DARK,
            bgcolor=style.PANEL_LIGHT,
            label_style=ft.TextStyle(color=style.TEXT_MUTED),
        )

        btn_atualizar = style.primary_button("Atualizar", icon=ft.Icons.REFRESH, on_click=lambda _: self._atualizar_logs())
        btn_voltar = style.ghost_button(
            "Voltar",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: self.voltar_callback() if callable(self.voltar_callback) else None,
        )

        layout = ft.Column(
            [
                title,
                ft.Text("Arquivo: " + self.log_path, color=style.TEXT_MUTED),
                ft.Row([btn_atualizar, btn_voltar], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                self.text_area,
            ],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.add(
            ft.Container(
                content=style.surface_container(layout, padding=28),
                padding=ft.Padding(24, 24, 24, 24),
                expand=True,
                alignment=ft.alignment.center,
            )
        )

    def _ler_logs(self):
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, "r", encoding="utf-8") as arquivo:
                    return arquivo.read()[-8000:]
            return "Nenhum log encontrado."
        except Exception as err:
            logger.error("Erro ao ler logs: %s", err)
            return f"Erro ao ler logs: {err}"

    def _atualizar_logs(self):
        self.text_area.value = self._ler_logs()
        self.page.update()
        logger.info("Logs atualizados.")
