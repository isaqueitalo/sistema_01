# APP/config.py
import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Diretório do banco
DATA_DIR = os.path.join(BASE_DIR, "DATA")
os.makedirs(DATA_DIR, exist_ok=True)

# Caminho completo do banco
DB_NAME = os.path.join(DATA_DIR, "usuarios.db")

# Configurações da interface
APP_TITLE = "🔐 Sistema de Login - SQLite"
WINDOW_SIZE = "400x400"
