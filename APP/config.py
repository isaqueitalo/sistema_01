# Caminho do banco de dados
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, "DATA", "usuarios.db")

# Configurações da interface
APP_TITLE = "🔐 Sistema de Login - SQLite"
WINDOW_SIZE = "400x400"

