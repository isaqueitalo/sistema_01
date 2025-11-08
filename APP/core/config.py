import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "..", "DATA")

DB_NAME = os.path.join(DATA_DIR, "sistema.db")
LOG_FILE = os.path.join(DATA_DIR, "system.log")
