
from APP.database import inicializar_banco
from APP.ui.login_ui import LoginUI
from APP.logger import logger   # ✅ Importa o logger centralizado
import ttkbootstrap as tb

if __name__ == "__main__":
    try:
        logger.info(">>> Inicializando sistema...")
        inicializar_banco()
        logger.info("Banco de dados inicializado com sucesso.")

        root = tb.Window(themename="cyborg")
        app = LoginUI(root)
        logger.info("Interface de login carregada. Aplicação iniciada.")
        root.mainloop()

    except Exception as e:
        logger.critical(f"Erro crítico ao iniciar o sistema: {e}", exc_info=True)
        print("Ocorreu um erro grave. Verifique o arquivo de log em DATA/system.log.")
