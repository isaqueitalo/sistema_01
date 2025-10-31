# main.py
from APP.database import inicializar_banco
from APP.ui import LoginApp
import tkinter as tk

if __name__ == "__main__":
    print(">>> Sistema iniciado.")
    inicializar_banco()

    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
