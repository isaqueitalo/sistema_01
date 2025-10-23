from APP.database import inicializar_banco
from APP.ui import LoginApp
import ttkbootstrap as tb  # Usando janela com tema moderno

if __name__ == "__main__":
    print(">>> Inicializando sistema de login...")
    inicializar_banco()  # Garante que o banco exista

    root = tb.Window(themename="cyborg")
    app = LoginApp(root)
    root.mainloop()
