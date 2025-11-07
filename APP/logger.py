import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# === Diretório do log ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "DATA")
os.makedirs(DATA_DIR, exist_ok=True)

LOG_FILE = os.path.join(DATA_DIR, "system.log")

# === Cria o logger principal ===
logger = logging.getLogger("sistema_logger")

# Evita criar handlers duplicados (caso o módulo seja importado várias vezes)
if not logger.handlers:
    logger.setLevel(logging.DEBUG)  # 🧠 Use INFO ou WARNING em produção

    # === Formato detalhado ===
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # === Handler de arquivo (com rotação) ===
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2_000_000,  # 2 MB por arquivo
        backupCount=5,       # mantém até 5 versões antigas
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # === Handler de console (para desenvolvimento) ===
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # === Adiciona os handlers ===
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # === Mensagem inicial ===
    logger.info("=== Logger inicializado ===")
    logger.info(f"Arquivo de log: {LOG_FILE}")

# === Função auxiliar opcional ===
def get_logger(name: str = None):
    """
    Retorna um logger nomeado (ex: logger para um módulo específico).
    Exemplo:
        from APP.logger import get_logger
        logger = get_logger(__name__)
    """
    return logger if not name else logging.getLogger(name)
