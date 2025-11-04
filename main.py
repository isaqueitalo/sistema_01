from APP.database import inicializar_banco
from APP.ui.login_ui import LoginUI 
import ttkbootstrap as tb

if __name__ == "__main__":
    print(">>> Inicializando sistema de login...")
    inicializar_banco()

    root = tb.Window(themename="cyborg")
    app = LoginUI(root) # 🚨 Nome da classe alterado
    root.mainloop()