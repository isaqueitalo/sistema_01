from APP.database import inicializar_banco
from APP.ui import LoginApp
import tkinter as tk

print(">>> Sistema iniciado. Criando janela Tkinter...")

if __name__ == "__main__":
    inicializar_banco()  # Garante que o banco exista
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
