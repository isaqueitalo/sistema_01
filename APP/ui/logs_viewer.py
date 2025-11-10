# APP/ui/logs_viewer.py
import flet as ft
import os
from APP.core.config import config
from APP.core.logger import logger


class LogsViewer:
    """Visualizador de logs do sistema (somente leitura)."""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.log_path = config.log_path  # ✅ novo atributo
        self.build_ui()
        logger.info("Tela de visualização de logs carregada.")

    def build_ui(self):
        """Monta a interface de visualização de logs."""
        self.page.clean()
        self.page.title = "Visualizador de Logs"

        title = ft.Text("🪵 Visualizador de Logs", size=22, weight=ft.FontWeight.BOLD)
        self.text_area = ft.TextField(
            multiline=True,
            read_only=True,
            width=700,
            height=400,
            border_color=ft.Colors.OUTLINE,
            border_radius=10,
            text_size=14,
            label="Conteúdo do Log",
            value=self._ler_logs(),
            color=ft.Colors.ON_SURFACE,
        )

        btn_atualizar = ft.ElevatedButton("🔄 Atualizar", on_click=lambda e: self._atualizar_logs())
        btn_voltar = ft.TextButton("⬅️ Voltar", on_click=lambda e: self.voltar_callback())

        self.page.add(
            ft.Column(
                [
                    title,
                    ft.Row([btn_atualizar, btn_voltar], alignment=ft.MainAxisAlignment.CENTER),
                    self.text_area,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            )
        )

    def _ler_logs(self):
        """Lê o conteúdo atual do arquivo de log."""
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, "r", encoding="utf-8") as f:
                    return f.read()[-5000:]  # lê as últimas 5000 linhas
            else:
                return "Nenhum log encontrado."
        except Exception as e:
            logger.error(f"Erro ao ler logs: {e}")
            return f"Erro ao ler logs: {e}"

    def _atualizar_logs(self):
        """Atualiza a área de texto com logs mais recentes."""
        self.text_area.value = self._ler_logs()
        self.page.update()
        logger.info("Logs atualizados na tela.")
