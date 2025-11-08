import sys
import flet as ft
from APP.core.database import inicializar_banco
from APP.core.logger import logger
from APP.ui.login_ui import LoginUI


def main(page: ft.Page):
    try:
        logger.info(">>> Inicializando o Sistema de Gestão com Flet...")
        inicializar_banco()

        page.title = "Sistema de Gestão - Login"
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.theme_mode = ft.ThemeMode.DARK

        LoginUI(page)
        logger.info("Tela de login carregada com sucesso.")
    except Exception as e:
        logger.critical(f"Erro crítico ao iniciar o sistema: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    ft.app(target=main)
