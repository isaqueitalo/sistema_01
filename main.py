import sys
import flet as ft
from APP.core.logger import logger
from APP.core.database import inicializar_banco
from APP.core.config import config
from APP.ui.login_ui import LoginUI
from APP.core.migrations import run_migrations

def run_app(page: ft.Page) -> None:
    try:
        logger.info(f">>> Inicializando o {config.app_name} com Flet...")

        # Configurações básicas da página
        page.title = config.app_name
        page.theme_mode = ft.ThemeMode.DARK if config.theme.lower() == "dark" else ft.ThemeMode.LIGHT
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.padding = 20

        # Inicializa banco e aplica migrações
        inicializar_banco()
        run_migrations()

        # Carrega tela de login
        LoginUI(page)
        logger.info("Tela de login carregada com sucesso.")

    except Exception as e:
        logger.critical(f"Erro crítico ao iniciar o sistema: {e}", exc_info=True)
        print(f"[ERRO FATAL] O sistema não pôde ser iniciado: {e}")
        sys.exit(1)

def main() -> None:
    try:
        ft.app(target=run_app)
    except KeyboardInterrupt:
        logger.info("Aplicação encerrada manualmente.")
    except Exception as e:
        logger.critical(f"Erro fatal na aplicação: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
